from sqlalchemy import func, select, case, and_, text
from werkzeug.exceptions import BadRequest

from db.constants import GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS
from db.enums import RequestStatus
from db.models.implementations.links.location__data_source_view import LinkLocationDataSourceView
from db.models.implementations.links.location__data_request import LinkLocationDataRequest
from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.location.expanded import LocationExpanded
from db.models.implementations.core.log.notification import NotificationLog
from db.queries.builder.core import QueryBuilderBase
from db.queries.ctes.dependent_location import DependentLocationCTE
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.util.env import get_env_variable


class GetMetricsFollowedSearchesBreakdownQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: MetricsFollowedSearchesBreakdownRequestDTO):
        super().__init__()
        self.dto = dto

    def run(self) -> list[dict[str, str | int | None | float]]:
        sortable_columns = GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS

        if self.dto.sort_by is not None:
            if self.dto.sort_by not in sortable_columns:
                raise BadRequest(
                    description=f"Invalid sort_by value: {self.dto.sort_by}; must be one of {sortable_columns}",
                )

        # Get last notification time
        last_notification_query = (
            select(NotificationLog.created_at)
            .order_by(NotificationLog.created_at.desc())
            .limit(1)
            .cte("last_notification")
        )

        last_notification = last_notification_query.c.created_at

        base_search_url = (
            f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/search/results?location_id="
        )

        def count_distinct(field, label):
            return func.count(func.distinct(field)).label(label)

        # Dependent Location CTE
        dlsq = DependentLocationCTE()

        def maybe_limit(column, limit_to_before_last_notification):
            """Maybe limit to before the last notification"""
            return (
                column < last_notification
                if limit_to_before_last_notification
                else True
            )

        def follower_count_subquery():
            link = LinkUserFollowedLocation
            return (
                select(
                    link.location_id.label("location_id"),
                    count_distinct(link.user_id, "total_count"),
                    count_distinct(
                        case(
                            (link.created_at < last_notification, link.user_id),
                        ),
                        "old_count",
                    ),
                )
                .join(dlsq.query, link.location_id == dlsq.dependent_location_id)
                .group_by(link.location_id)
                .cte("follow_counts")
            )

        def source_count_subquery():
            link = LinkLocationDataSourceView
            ds = DataSource
            return (
                select(
                    dlsq.location_id.label("location_id"),
                    count_distinct(ds.id, "total_count"),
                    count_distinct(
                        case((ds.created_at < last_notification, ds.id)),
                        "old_count",
                    ),
                )
                .join(link, link.location_id == dlsq.dependent_location_id)
                .join(ds, ds.id == link.data_source_id)
                .group_by(dlsq.location_id)
                .cte("source_counts")
            )

        def requests_col(request_status: RequestStatus, limit: bool, label: str):
            dr = DataRequest
            return count_distinct(
                case(
                    (
                        and_(
                            dr.request_status == request_status.value,
                            maybe_limit(dr.date_status_last_changed, limit),
                        ),
                        dr.id,
                    )
                ),
                label=f"{label}_count",
            )

        def requests_count_subquery():
            dr = DataRequest
            rs = RequestStatus
            link = LinkLocationDataRequest
            return (
                select(
                    dlsq.location_id,
                    requests_col(rs.READY_TO_START, False, "total_approved"),
                    requests_col(rs.READY_TO_START, True, "old_approved"),
                    requests_col(rs.COMPLETE, False, "total_complete"),
                    requests_col(rs.COMPLETE, True, "old_complete"),
                )
                .join(link, link.location_id == dlsq.dependent_location_id)
                .join(dr, dr.id == link.data_request_id)
                .group_by(dlsq.location_id)
                .cte("request_counts")
            )

        def get_diff_v2(attr1, attr2, attribute_name):
            return (func.coalesce(attr1, 0) - func.coalesce(attr2, 0)).label(
                f"{attribute_name}_change"
            )

        follows = follower_count_subquery()
        diff_follows = get_diff_v2(
            follows.c.total_count, follows.c.old_count, "follower"
        )

        sources = source_count_subquery()
        diff_sources = get_diff_v2(sources.c.total_count, sources.c.old_count, "source")

        requests = requests_count_subquery()
        diff_approved_requests = get_diff_v2(
            requests.c.total_approved_count,
            requests.c.old_approved_count,
            "approved_requests",
        )
        diff_completed_requests = get_diff_v2(
            requests.c.total_complete_count,
            requests.c.old_complete_count,
            "completed_requests",
        )

        def coalesce(attr, label):
            return func.coalesce(attr, 0).label(label)

        final_query = (
            select(
                follows.c.location_id,
                LocationExpanded.full_display_name.label("location_name"),
                coalesce(follows.c.total_count, "follower_count"),
                diff_follows,
                coalesce(sources.c.total_count, "source_count"),
                diff_sources,
                coalesce(requests.c.total_approved_count, "approved_requests_count"),
                diff_approved_requests,
                coalesce(requests.c.total_complete_count, "completed_requests_count"),
                diff_completed_requests,
                func.concat(base_search_url, LocationExpanded.id).label("search_url"),
            )
            .select_from(follows)
            .join(LocationExpanded, follows.c.location_id == LocationExpanded.id)
        )

        for subquery in [sources, requests]:
            final_query = final_query.outerjoin(
                subquery,
                follows.c.location_id == subquery.c.location_id,
            )

        # The follower count must be nonzero
        final_query = final_query.where(
            follows.c.total_count > 0,
        )

        if self.dto.sort_by is not None:
            final_query = final_query.order_by(
                text(f"{self.dto.sort_by} {self.dto.sort_order.value}")
            )
        final_query = final_query.limit(100).offset((self.dto.page - 1) * 100)

        raw_results = self.session.execute(final_query).all()

        results = []
        for result in raw_results:
            d = {
                "location_name": result.location_name,
                "location_id": result.location_id,
                "follower_count": result.follower_count,
                "follower_change": result.follower_change,
                "source_count": result.source_count,
                "source_change": result.source_change,
                "approved_requests_count": result.approved_requests_count,
                "approved_requests_change": result.approved_requests_change,
                "completed_requests_count": result.completed_requests_count,
                "completed_requests_change": result.completed_requests_change,
                "search_url": result.search_url,
            }
            results.append(d)

        return results
