from typing import final, Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.enums import ExternalAccountTypeEnum, LocationType, UserCapacityEnum, RequestStatus, RequestUrgency
from db.helpers_.result_formatting import get_display_name
from db.models.implementations import LinkUserFollowedLocation
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
from endpoints.instantiations.data_requests_._shared.dtos.get import DataRequestsGetDTOBase, DataSourceLimitedDTO
from endpoints.instantiations.data_requests_.get.many.dtos.response import GetManyDataRequestsResponseDTO
from endpoints.instantiations.locations_._shared.dtos.response import LocationInfoResponseDTO
from endpoints.instantiations.search._shared.dtos.follow import GetUserFollowedSearchesDTO, FollowSearchResponseDTO
from endpoints.instantiations.user._shared.dtos.recent_searches import GetUserRecentSearchesDTO
from endpoints.instantiations.user.by_id.get.dto import UserProfileResponseSchemaInnerDTO, ExternalAccountDTO
from endpoints.instantiations.user.by_id.get.recent_searches.dto import GetUserRecentSearchesOuterDTO
from middleware.enums import PermissionsEnum, RecordTypes
from utilities.enums import RecordCategoryEnum


@final
class GetUserByIdQueryBuilder(QueryBuilderBase):

    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id

    def run(self) -> UserProfileResponseSchemaInnerDTO:
        query = (
            select(User)
            .where(User.id == self.user_id)
            .options(
                selectinload(User.external_accounts),
                selectinload(User.capacities),

                selectinload(User.recent_searches)
                .selectinload(RecentSearch.location)
                .selectinload(Location.state),

                selectinload(User.recent_searches)
                .selectinload(RecentSearch.location)
                .selectinload(Location.county),

                selectinload(User.recent_searches)
                .selectinload(RecentSearch.location)
                .selectinload(Location.locality),

                selectinload(User.recent_searches)
                .selectinload(RecentSearch.record_categories),

                selectinload(User.follows)
                .selectinload(LinkUserFollowedLocation.record_types)
                .selectinload(RecordType.record_category),

                selectinload(User.follows)
                .selectinload(LinkUserFollowedLocation.location)
                .selectinload(Location.state),

                selectinload(User.follows)
                .selectinload(LinkUserFollowedLocation.location)
                .selectinload(Location.county),

                selectinload(User.follows)
                .selectinload(LinkUserFollowedLocation.location)
                .selectinload(Location.locality),

                selectinload(User.data_requests)
                .selectinload(DataRequest.data_sources),

                selectinload(User.data_requests)
                .selectinload(DataRequest.locations),

                selectinload(User.data_requests)
                .selectinload(DataRequest.github_issue_info),

                selectinload(User.permissions),
            )
        )

        user = self.session.execute(query).scalars().one()
        return UserProfileResponseSchemaInnerDTO(
            email=user.email,
            external_accounts=self._process_external_accounts(user.external_accounts),
            recent_searches=self._process_recent_searches(user.recent_searches),
            followed_searches=self._process_follows(user.follows),
            data_requests=self._process_data_requests(user.data_requests),
            permissions=[PermissionsEnum(permission.permission_name) for permission in user.permissions],
            capacities=[UserCapacityEnum(capacity.name) for capacity in user.capacities],
        )

    def _process_external_accounts(
        self,
        external_accounts: list[ExternalAccount]
    ) -> ExternalAccountDTO:

        github_account = None
        for external_account in external_accounts:
            if external_account.account_type == ExternalAccountTypeEnum.GITHUB.value:
                github_account = external_account.account_identifier
        return ExternalAccountDTO(
            github=github_account
        )

    def _process_recent_searches(
        self,
        recent_searches: list[RecentSearch]
    ) -> GetUserRecentSearchesOuterDTO:
        results: list[GetUserRecentSearchesDTO] = []
        for recent_search in recent_searches:
            location: Location = recent_search.location
            state: USState = location.state
            county: County = location.county
            locality: Locality = location.locality

            record_categories: list[RecordCategory] = recent_search.record_categories
            rc_enums: list[RecordCategoryEnum] = []
            for record_category in record_categories:
                rc_enums.append(RecordCategoryEnum(record_category.name))


            dto = GetUserRecentSearchesDTO(
                location_id=location.id,
                state_name=state.state_name if state else None,
                county_name=county.name if county else None,
                locality_name=locality.name if locality else None,
                location_type=location.type,
                record_categories=rc_enums
            )
            results.append(dto)

        return GetUserRecentSearchesOuterDTO(
            data=results
        )

    def _process_follows(
        self,
        follows: list[LinkUserFollowedLocation]
    ) -> GetUserFollowedSearchesDTO:
        results: list[FollowSearchResponseDTO] = []
        for follow in follows:
            location = follow.location
            state = location.state
            county = location.county
            locality = location.locality

            subscriptions_by_category: dict[str, str] = {}
            for record_type in follow.record_types:
                record_category_name = record_type.record_category.name
                record_type_name = record_type.name
                subscriptions_by_category[record_category_name] = record_type_name

            dto = FollowSearchResponseDTO(
                location_id=location.id,
                display_name=get_display_name(
                    location_type=LocationType(location.type),
                    state_name=state.state_name if state else None,
                    county_name=county.name if county else None,
                    locality_name=locality.name if locality else None,
                ),
                state_name=state.state_name if state else None,
                county_name=county.name if county else None,
                locality_name=locality.name if locality else None,
                subscriptions_by_category=subscriptions_by_category
            )
            results.append(dto)

        return GetUserFollowedSearchesDTO(
            data=results
        )



    def _process_data_requests(
        self,
        data_requests: list[DataRequest]
    ) -> GetManyDataRequestsResponseDTO:
        results: list[DataRequestsGetDTOBase] = []
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
                        location_id=location.id
                    )
                )
                loc_ids.append(location.id)

            github_issue_info = data_request.github_issue_info

            dto = DataRequestsGetDTOBase(

                # Core fields
                id=data_request.id,
                title=data_request.title,
                submission_notes=data_request.submission_notes,
                request_status=RequestStatus(data_request.request_status),
                archive_reason=data_request.archive_reason,
                date_created=data_request.date_created,
                date_status_last_changed=data_request.date_status_last_changed,
                creator_user_id=data_request.creator_user_id,
                internal_notes=data_request.internal_notes,
                record_types_required=[RecordTypes(rt) for rt in data_request.record_types_required],
                pdap_response=data_request.pdap_response,
                coverage_range=data_request.coverage_range,
                data_requirements=data_request.data_requirements,
                request_urgency=RequestUrgency(data_request.request_urgency),

                # Github fields
                github_issue_url=github_issue_info.github_issue_url if github_issue_info else None,
                github_issue_number=github_issue_info.github_issue_number if github_issue_info else None,

                # Nested fields
                data_sources=ds_results,
                data_source_ids=ds_ids,
                locations=loc_results,
                location_ids=loc_ids
            )
            results.append(dto)

        return GetManyDataRequestsResponseDTO(
            data=results
        )
