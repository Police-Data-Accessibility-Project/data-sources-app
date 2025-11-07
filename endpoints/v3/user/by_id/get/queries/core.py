from typing import final

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.enums import (
    ExternalAccountTypeEnum,
    LocationType,
    UserCapacityEnum,
    RequestStatus,
    RequestUrgency,
)
from db.helpers_.result_formatting import get_display_name
from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.external_account import ExternalAccount
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.expanded import LocationExpanded
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.core.recent_search.core import RecentSearch
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.data_requests_._shared.dtos.get import (
    DataSourceLimitedDTO,
)
from endpoints.instantiations.locations_._shared.dtos.response import (
    LocationInfoResponseDTO,
)
from endpoints.instantiations.search._shared.dtos.follow import (
    GetUserFollowedSearchesDTO,
)
from endpoints.instantiations.user.by_id.get.recent_searches.dto import (
    GetUserRecentSearchesOuterDTO,
)
from endpoints.v3.user.by_id.get.response.core import GetUserProfileResponse
from endpoints.v3.user.by_id.get.response.data_request import GetDataRequestModel, GetDataRequestInfoModel
from endpoints.v3.user.by_id.get.response.external_accounts import ExternalAccountsModel
from endpoints.v3.user.by_id.get.response.followed_search import GetUserFollowedSearchModel
from endpoints.v3.user.by_id.get.response.location import GetUserSearchLocationModel
from endpoints.v3.user.by_id.get.response.recent_search import GetUserRecentSearchModel
from middleware.enums import PermissionsEnum, RecordTypesEnum
from utilities.enums import RecordCategoryEnum


@final
class GetUserByIdQueryBuilder(QueryBuilderBase):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id

    def run(self) -> GetUserProfileResponse:
        query = (
            select(User)
            .where(User.id == self.user_id)
            .options(
                # Simple one-hop relations
                selectinload(User.external_accounts),
                selectinload(User.capacities),
                selectinload(User.permissions),

                # Recent searches: record categories + location pieces
                selectinload(User.recent_searches).options(
                    selectinload(RecentSearch.record_categories),
                    selectinload(RecentSearch.record_types),
                    selectinload(RecentSearch.location).options(
                        selectinload(Location.state),
                        selectinload(Location.county),
                        selectinload(Location.locality),
                    ),
                ),

                # Follows: record types -> category, plus location pieces
                selectinload(User.follows).options(
                    selectinload(LinkUserFollowedLocation.record_types)
                    .selectinload(RecordType.record_category),
                    selectinload(LinkUserFollowedLocation.location).options(
                        selectinload(Location.state),
                        selectinload(Location.county),
                        selectinload(Location.locality),
                    ),
                    ),

                # Data requests: data sources, locations, GitHub info
                selectinload(User.data_requests).options(
                    selectinload(DataRequest.data_sources),
                    selectinload(DataRequest.locations),
                    selectinload(DataRequest.github_issue_info),
                ),
            )
        )

        user = self.session.execute(query).scalars().one()
        return GetUserProfileResponse(
            email=user.email,
            external_accounts=self._process_external_accounts(user.external_accounts),
            recent_searches=self._process_recent_searches(user.recent_searches),
            followed_searches=self._process_follows(user.follows),
            data_requests=self._process_data_requests(user.data_requests),
            permissions=[
                PermissionsEnum(permission.permission_name)
                for permission in user.permissions
            ],
            capacities=[
                UserCapacityEnum(capacity.capacity) for capacity in user.capacities
            ],
        )

    def _process_external_accounts(
        self, external_accounts: list[ExternalAccount]
    ) -> ExternalAccountsModel:
        github_account = None
        for external_account in external_accounts:
            if external_account.account_type == ExternalAccountTypeEnum.GITHUB.value:
                github_account = external_account.account_identifier
        return ExternalAccountsModel(github=github_account)

    def _process_recent_searches(
        self, recent_searches: list[RecentSearch]
    ) -> list[GetUserRecentSearchModel]:
        results: list[GetUserRecentSearchModel] = []
        for recent_search in recent_searches:
            location: Location | None = recent_search.location
            state: USState | None = location.state if location else None
            county: County | None = location.county if location else None
            locality: Locality | None = location.locality if location else None
            if location is not None:
                display_name = get_display_name(
                    location_type=LocationType(location.type),
                    state_name=state.state_name if state else None,
                    county_name=county.name if county else None,
                    locality_name=locality.name if locality else None,
                ),
            else:
                display_name = ""

            record_types: list[RecordType] = recent_search.record_types
            rt_enums: list[RecordTypesEnum] = []
            for record_type in record_types:
                rt_enums.append(RecordTypesEnum(record_type.name))

            record_categories: list[RecordCategory] = recent_search.record_categories
            rc_enums: list[RecordCategoryEnum] = []
            for record_category in record_categories:
                rc_enums.append(RecordCategoryEnum(record_category.name))

            result = GetUserRecentSearchModel(
                location_info=GetUserSearchLocationModel(
                    location_id=location.id if location else None,
                    state_name=state.state_name if state else None,
                    county_name=county.name if county else None,
                    locality_name=locality.name if locality else None,
                    location_type=location.type if location else None,
                ),
                record_categories=rc_enums,
                record_types=rt_enums,
                display_name=display_name,
                search_date=recent_search.created_at,
            )
            results.append(result)

        return GetUserRecentSearchesOuterDTO(data=results)

    def _process_follows(
        self, follows: list[LinkUserFollowedLocation]
    ) -> list[GetUserFollowedSearchModel]:
        results: list[GetUserFollowedSearchModel] = []
        for follow in follows:
            location = follow.location
            state = location.state
            county = location.county
            locality = location.locality

            subscriptions_by_category: dict[str, str] = {}
            record_types: list[RecordTypesEnum] = []
            record_categories: list[RecordCategoryEnum] = []
            for record_type in follow.record_types:
                record_category_name = record_type.record_category.name
                record_type_name = record_type.name
                record_types.append(RecordTypesEnum(record_type_name))
                record_categories.append(RecordCategoryEnum(record_category_name))
                subscriptions_by_category[record_category_name] = record_type_name

            result = GetUserFollowedSearchModel(
                display_name=get_display_name(
                    location_type=LocationType(location.type),
                    state_name=state.state_name if state else None,
                    county_name=county.name if county else None,
                    locality_name=locality.name if locality else None,
                ),
                location_info=GetUserSearchLocationModel(
                    location_id=location.id,
                    state_name=state.state_name if state else None,
                    county_name=county.name if county else None,
                    locality_name=locality.name if locality else None,
                    location_type=location.type if location else None,
                ),
                record_types_by_category = subscriptions_by_category,
                record_types=record_types,
                record_categories=record_categories,
            )
            results.append(result)

        return GetUserFollowedSearchesDTO(data=results)

    def _process_data_requests(
        self, data_requests: list[DataRequest]
    ) -> list[GetDataRequestModel]:
        results: list[GetDataRequestModel] = []
        for data_request in data_requests:
            data_sources: list[DataSource] = data_request.data_sources
            ds_results: list[DataSourceLimitedDTO] = []
            ds_ids: list[int] = []
            for data_source in data_sources:
                ds_results.append(
                    DataSourceLimitedDTO(
                        id=data_source.id,
                        name=data_source.name,
                    )
                )
                ds_ids.append(data_source.id)

            locations: list[LocationExpanded] = data_request.locations
            loc_results: list[LocationInfoResponseDTO] = []
            loc_ids: list[int] = []
            for location in locations:
                loc_results.append(
                    LocationInfoResponseDTO(
                        type=LocationType(location.type),
                        state_name=location.state_name,
                        state_iso=location.state_iso,
                        county_name=location.county_name,
                        county_fips=location.county_fips,
                        locality_name=location.locality_name,
                        display_name=location.display_name,
                        location_id=location.id,
                    )
                )
                loc_ids.append(location.id)

            github_issue_info = data_request.github_issue_info

            dto = GetDataRequestModel(
                # Core fields
                info=GetDataRequestInfoModel(
                    id=data_request.id,
                    title=data_request.title,
                    submission_notes=data_request.submission_notes,
                    request_status=RequestStatus(data_request.request_status),
                    archive_reason=data_request.archive_reason,
                    date_created=data_request.date_created,
                    date_status_last_changed=data_request.date_status_last_changed,
                    creator_user_id=data_request.creator_user_id,
                    internal_notes=data_request.internal_notes,
                    record_types_required=[
                        RecordTypesEnum(rt) for rt in data_request.record_types_required
                    ],
                    pdap_response=data_request.pdap_response,
                    coverage_range=data_request.coverage_range,
                    data_requirements=data_request.data_requirements,
                    request_urgency=RequestUrgency(data_request.request_urgency),
                    # Github fields
                    github_issue_url=github_issue_info.github_issue_url
                    if github_issue_info
                    else None,
                    github_issue_number=github_issue_info.github_issue_number
                    if github_issue_info
                    else None,
                ),
                # Nested fields
                data_sources=ds_results,
                data_source_ids=ds_ids,
                locations=loc_results,
                location_ids=loc_ids,
            )
            results.append(dto)

        return results
