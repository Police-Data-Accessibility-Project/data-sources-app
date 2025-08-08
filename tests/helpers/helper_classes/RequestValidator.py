"""
Class based means to run and validate requests
"""

from datetime import datetime
from http import HTTPStatus
from typing import Optional, Type, Union, List

from flask.testing import FlaskClient
from marshmallow import Schema

from db.constants import PAGE_SIZE
from db.enums import (
    SortOrder,
    RequestStatus,
    ApprovalStatus,
    UpdateFrequency,
)
from endpoints.instantiations.source_collector.agencies.sync.schema_config import (
    SourceCollectorSyncAgenciesSchemaConfig,
)
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestDTO,
)
from endpoints.instantiations.source_collector.agencies.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from endpoints.schema_config.instantiations.admin.users.by_id.delete import (
    AdminUsersByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.by_id.get import (
    AdminUsersByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.by_id.put import (
    AdminUsersByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.get_many import (
    AdminUsersGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.post import (
    AdminUsersPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.get import (
    AgenciesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.get_many import (
    AgenciesGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.archives.get import (
    ArchivesGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.login import LoginEndpointSchemaConfig
from endpoints.schema_config.instantiations.data_requests.by_id.get import (
    DataRequestsByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.by_id.withdraw import (
    DataRequestsByIDWithdrawEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.get_many import (
    DataRequestsGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.delete import (
    DataRequestsRelatedLocationsDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.post import (
    DataRequestsRelatedLocationsPostEndpointSchemaConfig,
)
from endpoints.instantiations.data_sources_.get.by_id.schema_config import DataSourcesByIDGetEndpointSchemaConfig
from endpoints.schema_config.instantiations.data_sources.by_id.reject import (
    DataSourcesByIDRejectEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.get_many import (
    DataSourcesGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.github.synchronize import (
    GitHubDataRequestsSynchronizePostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.by_id.get import (
    LocationsByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.by_id.put import (
    LocationsByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.data_requests import (
    LocationsRelatedDataRequestsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.get_many import (
    LocationsGetManyEndpointSchemaConfig,
)
from endpoints.instantiations.map.locations.schema_config import (
    LocationsMapEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.match import MatchAgencyEndpointSchemaConfig
from endpoints.schema_config.instantiations.metrics.followed_searches.aggregate import (
    MetricsFollowedSearchesAggregateGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.metrics.followed_searches.breakdown import (
    MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.metrics.get import (
    MetricsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.proposal_agencies import (
    ProposalAgenciesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.record_type_and_category import (
    RecordTypeAndCategoryGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.reset_password.request import (
    RequestResetPasswordEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.federal import (
    SearchFederalGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.delete import (
    SearchFollowDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.get import (
    SearchFollowGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.national import (
    SearchFollowNationalEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.post import (
    SearchFollowPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.location_and_record_type import (
    SearchLocationAndRecordTypeGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.source_collector.data_sources import (
    SourceCollectorDataSourcesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.source_collector.duplicates import (
    SourceCollectorDuplicatesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.typeahead.agencies import (
    TypeaheadAgenciesEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.profile.data_requests import (
    UserProfileDataRequestsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.profile.get import (
    UserProfileGetEndpointSchemaConfig,
)
from middleware.constants import DATE_FORMAT
from middleware.enums import OutputFormatEnum, RecordTypes
from middleware.schema_and_dto.dtos.locations.get import LocationsGetRequestDTO
from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.util.dict import update_if_not_none
from tests.helpers.common_test_data import get_test_name
from tests.helpers.constants import (
    DATA_REQUESTS_BY_ID_ENDPOINT,
    AGENCIES_BASE_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_LOCATIONS_ENDPOINT,
    DATA_SOURCES_BASE_ENDPOINT,
)
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.helper_functions_simple import (
    get_authorization_header,
    add_query_params,
)
from tests.helpers.run_and_validate_request import (
    run_and_validate_request,
)
from utilities.enums import RecordCategoryEnum


class RequestValidator:
    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client

    def post(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def get(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="get",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def put(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def delete(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="delete",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def patch(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="patch",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    # Below are shorthands for common requests

    def login(
        self,
        email: str,
        password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Schema = LoginEndpointSchemaConfig.primary_output_schema,
    ):
        return self.post(
            endpoint="/api/auth/login",
            json={
                "email": email,
                "password": password,
            },
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
        )

    def reset_password(
        self,
        token: str,
        password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return self.post(
            endpoint="/api/auth/reset-password",
            headers=get_authorization_header(scheme="Bearer", token=token),
            json={"password": password},
            expected_response_status=expected_response_status,
        )

    def request_reset_password(
        self,
        email: str,
        mocker,
        expect_call: bool = True,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        mock = mocker.patch(
            "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
        )
        self.post(
            endpoint="/api/auth/request-reset-password",
            json={"email": email},
            expected_response_status=expected_response_status,
            expected_schema=RequestResetPasswordEndpointSchemaConfig.primary_output_schema,
        )
        if not expect_call:
            assert not mock.called
            return
        assert mock.call_args[1]["email"] == email
        return mock.call_args[1]["token"]

    def reset_token_validation(
        self,
        token: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        return self.post(
            endpoint="/api/auth/reset-token-validation",
            headers=get_authorization_header(scheme="Bearer", token=token),
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def get_permissions(
        self,
        user_email: str,
        headers: dict,
        expected_json_content: Optional[dict] = None,
    ):
        endpoint = f"/permissions?user_email={user_email}"
        return self.get(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
        )

    def update_permissions(
        self,
        user_email: str,
        headers: dict,
        action: str,
        permission: str,
    ):
        endpoint = f"/permissions?user_email={user_email}"
        return self.put(
            endpoint=endpoint,
            headers=headers,
            json={"action": action, "permission": permission},
        )

    def search(
        self,
        headers: dict,
        location_id: int,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        format: Optional[OutputFormatEnum] = OutputFormatEnum.JSON,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema: Optional[
            Union[Type[Schema], Schema]
        ] = SearchLocationAndRecordTypeGetEndpointSchemaConfig.primary_output_schema,
        expected_json_content: Optional[dict] = None,
    ):
        endpoint_base = "/search/search-location-and-record-type"
        query_params = self._get_search_query_params(
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        query_params.update({} if format is None else {"output_format": format.value})
        endpoint = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        kwargs = {"return_json": True if format == OutputFormatEnum.JSON else False}
        return self.get(
            endpoint=endpoint,
            headers=headers,
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            **kwargs,
        )

    def archives_get(
        self,
        headers: dict,
        update_frequency: Optional[UpdateFrequency] = None,
        last_archived_before: Optional[datetime] = None,
        page: int = 1,
    ):
        endpoint_base = "/archives"
        if last_archived_before is not None:
            last_archived_before = last_archived_before.strftime(DATE_FORMAT)

        params = {}
        d = {
            "update_frequency": update_frequency,
            "last_archived_before": last_archived_before,
            "page": page,
        }
        update_if_not_none(dict_to_update=params, secondary_dict=d)
        url = add_query_params(
            url=endpoint_base,
            params=params,
        )
        return self.get(
            endpoint=url,
            expected_schema=ArchivesGetEndpointSchemaConfig.primary_output_schema,
            headers=headers,
        )

    def federal_search(
        self,
        headers: dict,
        page: int = 1,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
    ):
        endpoint_base = "/search/federal"
        query_params = {"page": page}
        if record_categories is not None:
            query_params["record_categories"] = ",".join(
                [rc.value for rc in record_categories]
            )
        url = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        return self.get(
            endpoint=url,
            headers=headers,
            expected_schema=SearchFederalGetEndpointSchemaConfig.primary_output_schema,
        )

    @staticmethod
    def _get_search_query_params(
        record_categories: Optional[list[RecordCategoryEnum]],
        location_id: Optional[int] = None,
        record_types: Optional[list[RecordTypes]] = None,
    ):
        if location_id is not None:
            query_params = {
                "location_id": location_id,
            }
        else:
            query_params = {}
        if record_categories is not None:
            query_params["record_categories"] = ",".join(
                [rc.value for rc in record_categories]
            )

        if record_types is not None:
            query_params["record_types"] = ",".join([rt.value for rt in record_types])
        return query_params

    def create_agency(
        self,
        headers: dict,
        agency_post_parameters: dict,
    ):
        return self.post(
            endpoint="/agencies",
            headers=headers,
            json=agency_post_parameters,
        )["id"]

    def create_data_source(
        self,
        headers: dict,
        source_url: str = "http://src1.com",
        name: str = get_test_name(),
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        **kwargs,
    ):
        return self.post(
            endpoint=DATA_SOURCES_BASE_ENDPOINT,
            headers=headers,
            json={
                "entry_data": {
                    "source_url": source_url,
                    "name": name,
                    "approval_status": approval_status.value,
                    **kwargs,
                }
            },
        )

    def follow_national_search(
        self,
        headers: dict,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        query_params = self._get_search_query_params(
            record_categories=record_categories,
            record_types=record_types,
        )
        endpoint = add_query_params(
            url="/api/search/follow/national",
            params=query_params,
        )

        return self.post(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SearchFollowNationalEndpointSchemaConfig.primary_output_schema,
        )

    def unfollow_national_search(
        self,
        headers: dict,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        query_params = self._get_search_query_params(
            record_categories=record_categories,
            record_types=record_types,
        )
        endpoint = add_query_params(
            url="/api/search/follow/national",
            params=query_params,
        )

        return self.delete(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SearchFollowNationalEndpointSchemaConfig.primary_output_schema,
        )

    def follow_search(
        self,
        headers: dict,
        location_id: int,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        endpoint_base = "/api/search/follow"
        query_params = self._get_search_query_params(
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        endpoint = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        return self.post(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SearchFollowPostEndpointSchemaConfig.primary_output_schema,
        )

    def unfollow_search(
        self,
        headers: dict,
        location_id: int,
        record_categories: Optional[list[RecordCategoryEnum]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        endpoint_base = "/api/search/follow"
        query_params = self._get_search_query_params(
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        endpoint = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        return self.delete(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SearchFollowDeleteEndpointSchemaConfig.primary_output_schema,
        )

    def get_followed_searches(
        self,
        headers: dict,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return self.get(
            endpoint="/api/search/follow",
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SearchFollowGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_user_by_id(
        self,
        headers: dict,
        user_id: int,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=UserProfileGetEndpointSchemaConfig.primary_output_schema,
    ):
        return self.get(
            endpoint=f"/api/user/{user_id}",
            headers=headers,
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
        )

    def update_data_request(
        self, data_request_id: int, headers: dict, entry_data: dict
    ):
        return self.put(
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=headers,
            json={"entry_data": entry_data},
        )

    def get_data_requests(
        self,
        headers: dict,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        request_statuses: Optional[list[RequestStatus]] = None,
        limit: Optional[int] = PAGE_SIZE,
    ):
        query_params = {}
        update_if_not_none(
            dict_to_update=query_params,
            secondary_dict={
                "sort_by": sort_by,
                "sort_order": sort_order.value if sort_order is not None else None,
                "request_statuses": (
                    [rs.value for rs in request_statuses]
                    if request_statuses is not None
                    else None
                ),
                "limit": limit,
            },
        )
        return self.get(
            endpoint="/api/data-requests",
            headers=headers,
            query_parameters=query_params,
            expected_schema=DataRequestsGetManyEndpointSchemaConfig.primary_output_schema,
        )

    def withdraw_request(
        self,
        data_request_id: int,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return self.post(
            endpoint="/api/data-requests/{data_request_id}/withdraw".format(
                data_request_id=data_request_id
            ),
            headers=headers,
            expected_response_status=expected_response_status,
            expected_schema=DataRequestsByIDWithdrawEndpointSchemaConfig.primary_output_schema,
        )

    def get_data_request_by_id(
        self,
        data_request_id: int,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=DataRequestsByIDGetEndpointSchemaConfig.primary_output_schema,
    ):
        return self.get(
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=headers,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
        )

    def link_data_request_with_location(
        self,
        data_request_id: int,
        location_id: int,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=DataRequestsRelatedLocationsPostEndpointSchemaConfig.primary_output_schema,
        expected_json_content: Optional[dict] = None,
    ):
        return self.post(
            endpoint=DATA_REQUESTS_POST_DELETE_RELATED_LOCATIONS_ENDPOINT.format(
                data_request_id=data_request_id, location_id=location_id
            ),
            headers=headers,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
            expected_json_content=expected_json_content,
        )

    def unlink_data_request_with_location(
        self,
        data_request_id: int,
        location_id: int,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=DataRequestsRelatedLocationsDeleteEndpointSchemaConfig.primary_output_schema,
        expected_json_content: Optional[dict] = None,
    ):
        return self.delete(
            endpoint=DATA_REQUESTS_POST_DELETE_RELATED_LOCATIONS_ENDPOINT.format(
                data_request_id=data_request_id, location_id=location_id
            ),
            headers=headers,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
            expected_json_content=expected_json_content,
        )

    def get_user_profile_data_requests(
        self,
        headers: dict,
        expected_json_content: Optional[dict] = None,
        limit: int = PAGE_SIZE,
    ):
        return self.get(
            endpoint=f"/api/user/data-requests?page=1&limit={limit}",
            headers=headers,
            expected_json_content=expected_json_content,
            expected_schema=UserProfileDataRequestsGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_agency(
        self,
        headers: dict,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        page: int = 1,
        limit: int = PAGE_SIZE,
        approval_status: Optional[ApprovalStatus] = None,
    ):
        params = {}
        update_if_not_none(
            dict_to_update=params,
            secondary_dict={
                "approval_status": (
                    approval_status.value if approval_status is not None else None
                ),
                "sort_by": sort_by,
                "sort_order": sort_order.value if sort_order is not None else None,
                "page": page,
                "limit": limit,
            },
        )

        url = add_query_params(
            url=AGENCIES_BASE_ENDPOINT,
            params=params,
        )
        return self.get(
            endpoint=url,
            headers=headers,
            expected_schema=AgenciesGetManyEndpointSchemaConfig.primary_output_schema,
        )

    def add_location_to_agency(self, headers: dict, agency_id: int, location_id: int):
        return self.post(
            endpoint=f"/api/agencies/{agency_id}/locations/{location_id}",
            headers=headers,
        )

    def remove_location_from_agency(
        self, headers: dict, agency_id: int, location_id: int
    ):
        return self.delete(
            endpoint=f"/api/agencies/{agency_id}/locations/{location_id}",
            headers=headers,
        )

    def update_password(
        self,
        headers: dict,
        old_password: str,
        new_password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return self.post(
            endpoint="/api/user/update-password",
            headers=headers,
            json={"old_password": old_password, "new_password": new_password},
            expected_response_status=expected_response_status,
        )

    def get_api_spec(
        self,
    ):
        return self.get(
            endpoint="/api/swagger.json",
        )

    def get_data_sources(
        self,
        headers: dict,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        page: int = 1,
        limit: int = PAGE_SIZE,
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
    ):
        query_params = {}
        update_if_not_none(
            dict_to_update=query_params,
            secondary_dict={
                "sort_by": sort_by,
                "sort_order": sort_order.value if sort_order is not None else None,
                "page": page,
                "limit": limit,
                "approval_status": approval_status.value,
            },
        )

        return self.get(
            endpoint=DATA_SOURCES_BASE_ENDPOINT,
            query_parameters=query_params,
            headers=headers,
            expected_schema=DataSourcesGetManyEndpointSchemaConfig.primary_output_schema,
        )

    def update_data_source(
        self,
        tus: TestUserSetup,
        data_source_id: int,
        entry_data: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        return self.put(
            endpoint=f"/api/data-sources/{data_source_id}",
            headers=tus.jwt_authorization_header,
            json={"entry_data": entry_data},
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def get_agency_by_id(self, headers: dict, id: int):
        return self.get(
            endpoint=f"/api/agencies/{id}",
            headers=headers,
            expected_schema=AgenciesByIDGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_data_source_by_id(self, headers: dict, id: int):
        return self.get(
            endpoint=f"/api/data-sources/{id}",
            headers=headers,
            expected_schema=DataSourcesByIDGetEndpointSchemaConfig.primary_output_schema,
        )

    def match_agency(
        self,
        headers: dict,
        name: str,
        state: Optional[str] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
    ):
        data = {
            "name": name,
        }
        update_if_not_none(
            dict_to_update=data,
            secondary_dict={
                "state": state,
                "county": county,
                "locality": locality,
            },
        )
        return self.post(
            endpoint="/api/match/agency",
            headers=headers,
            json=data,
            expected_schema=MatchAgencyEndpointSchemaConfig.primary_output_schema,
        )

    # region Locations

    def get_location_by_id(
        self,
        headers: dict,
        location_id: int,
        expected_json_content: Optional[dict] = None,
    ):
        return self.get(
            endpoint=f"/api/locations/{location_id}",
            headers=headers,
            expected_schema=LocationsByIDGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_location_related_data_requests(
        self,
        headers: dict,
        location_id: int,
    ):
        return self.get(
            endpoint=f"/api/locations/{location_id}/data-requests",
            headers=headers,
            expected_schema=LocationsRelatedDataRequestsGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_metrics(
        self,
        headers: dict,
    ):
        return self.get(
            endpoint="/api/metrics",
            headers=headers,
            expected_schema=MetricsGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_user_by_id_admin(self, headers: dict, user_id: str):
        return self.get(
            endpoint=f"/api/admin/users/{user_id}",
            headers=headers,
            expected_schema=AdminUsersByIDGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_users(self, headers: dict, page: int = 1):
        return self.get(
            endpoint=f"/api/admin/users?page={page}",
            headers=headers,
            expected_schema=AdminUsersGetManyEndpointSchemaConfig.primary_output_schema,
        )

    def create_user(
        self,
        headers: dict,
        email: str,
        password: str,
        permissions: List[str],
    ):
        return self.post(
            endpoint="/api/admin/users",
            headers=headers,
            json={
                "email": email,
                "password": password,
                "permissions": permissions,
            },
            expected_schema=AdminUsersPostEndpointSchemaConfig.primary_output_schema,
        )

    def delete_user(self, headers: dict, user_id: str):
        return self.delete(
            endpoint=f"/api/admin/users/{user_id}",
            headers=headers,
            expected_schema=AdminUsersByIDDeleteEndpointSchemaConfig.primary_output_schema,
        )

    def update_admin_user(self, headers: dict, resource_id: str, password: str):
        return self.put(
            endpoint=f"/api/admin/users/{resource_id}",
            headers=headers,
            json={"password": password},
            expected_schema=AdminUsersByIDPutEndpointSchemaConfig.primary_output_schema,
        )

    def get_record_types_and_categories(self, headers: dict):
        return self.get(
            endpoint="/api/metadata/record-types-and-categories",
            headers=headers,
            expected_schema=RecordTypeAndCategoryGetEndpointSchemaConfig.primary_output_schema,
        )

    # endregion

    def github_data_requests_issues_synchronize(
        self,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ) -> dict:
        return self.post(
            endpoint="/api/github/data-requests/synchronize",
            headers=headers,
            expected_schema=GitHubDataRequestsSynchronizePostEndpointSchemaConfig.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def typeahead_agency(self, query: str):
        return self.get(
            endpoint=f"/api/typeahead/agencies?query={query}",
            expected_schema=TypeaheadAgenciesEndpointSchemaConfig.primary_output_schema,
        )

    def create_proposal_agency(
        self,
        headers: dict,
        data: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        return self.post(
            endpoint="/api/proposals/agencies",
            headers=headers,
            json=data,
            expected_schema=ProposalAgenciesPostEndpointSchemaConfig.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def reject_data_source(
        self,
        headers: dict,
        data_source_id: int,
        rejection_note: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Schema = DataSourcesByIDRejectEndpointSchemaConfig.primary_output_schema,
    ):
        return self.post(
            endpoint=f"/api/data-sources/{data_source_id}/reject",
            headers=headers,
            json={"rejection_note": rejection_note},
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def source_collector_data_sources(
        self,
        headers: dict,
        dto: SourceCollectorPostRequestDTO,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema: Schema = SourceCollectorDataSourcesPostEndpointSchemaConfig.primary_output_schema,
    ):
        return self.post(
            endpoint="/api/source-collector/data-sources",
            headers=headers,
            json=dto.model_dump(mode="json"),
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
        )

    def update_location(
        self,
        headers: dict,
        location_id: int,
        dto: LocationPutDTO,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        return self.put(
            endpoint=f"/api/locations/{location_id}",
            headers=headers,
            json=dto.model_dump(mode="json"),
            expected_schema=LocationsByIDPutEndpointSchemaConfig.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def get_locations_map(
        self, headers: dict, expected_json_content: Optional[dict] = None
    ):
        return self.get(
            endpoint="/api/map/locations",
            headers=headers,
            expected_schema=LocationsMapEndpointSchemaConfig.primary_output_schema,
            expected_json_content=expected_json_content,
        )

    def get_many_locations(
        self,
        headers: dict,
        dto: LocationsGetRequestDTO,
        expected_json_content: Optional[dict] = None,
    ):
        return self.get(
            endpoint="/api/locations",
            headers=headers,
            query_parameters=dto.model_dump(mode="json"),
            expected_schema=LocationsGetManyEndpointSchemaConfig.primary_output_schema,
            expected_json_content=expected_json_content,
        )

    def get_metrics_followed_searches_breakdown(
        self, headers: dict, dto: MetricsFollowedSearchesBreakdownRequestDTO
    ):
        return self.get(
            endpoint="/api/metrics/followed-searches/breakdown",
            headers=headers,
            query_parameters=dto.model_dump(mode="json"),
            expected_schema=MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig.primary_output_schema,
        )

    def get_metrics_followed_searches_aggregate(self, headers: dict):
        return self.get(
            endpoint="/api/metrics/followed-searches/aggregate",
            headers=headers,
            expected_schema=MetricsFollowedSearchesAggregateGetEndpointSchemaConfig.primary_output_schema,
        )

    def post_source_collector_duplicates(self, headers: dict, urls: List[str]):
        return self.post(
            endpoint="/api/source-collector/data-sources/duplicates",
            headers=headers,
            json={"urls": urls},
            expected_schema=SourceCollectorDuplicatesPostEndpointSchemaConfig.primary_output_schema,
        )

    def get_agencies_for_sync(
        self, headers: dict, dto: SourceCollectorSyncAgenciesRequestDTO
    ):
        return self.get(
            endpoint="/api/source-collector/agencies/sync",
            headers=headers,
            query_parameters=dto.model_dump(mode="json"),
            expected_schema=SourceCollectorSyncAgenciesSchemaConfig.primary_output_schema,
        )
