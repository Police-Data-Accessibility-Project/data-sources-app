"""
Class based means to run and validate requests
"""

from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from io import BytesIO
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
from middleware.enums import OutputFormatEnum, RecordTypes
from middleware.schema_and_dto_logic.dtos.locations.get import LocationsGetRequestDTO
from middleware.schema_and_dto_logic.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto_logic.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.schema_and_dto_logic.dtos.source_collector.post.request import (
    SourceCollectorPostRequestDTO,
)
from middleware.util.dict import update_if_not_none
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BY_ID_ENDPOINT,
    AGENCIES_BASE_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_LOCATIONS_ENDPOINT,
    DATA_SOURCES_BASE_ENDPOINT,
)
from tests.helper_scripts.helper_functions_simple import (
    get_authorization_header,
    add_query_params,
)
from tests.helper_scripts.run_and_validate_request import (
    run_and_validate_request,
)
from utilities.enums import RecordCategories


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

    # Below are shorthands for common requests

    def login(
        self,
        email: str,
        password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Schema = SchemaConfigs.LOGIN_POST.value.primary_output_schema,
    ):
        return self.post(
            endpoint="/api/auth/login",
            json={"email": email, "password": password},
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
        response = self.post(
            endpoint="/api/auth/request-reset-password",
            json={"email": email},
            expected_response_status=expected_response_status,
            expected_schema=SchemaConfigs.REQUEST_RESET_PASSWORD.value.primary_output_schema,
        )
        if not expect_call:
            assert not mock.called
            return
        assert mock.call_args[1]["email"] == email
        return mock.call_args[1]["token"]

    def signup(
        self,
        email: str,
        password: str,
        mocker,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        mock = mocker.patch("middleware.primary_resource_logic.signup.send_signup_link")
        self.post(
            endpoint="/api/auth/signup",
            json={"email": email, "password": password},
            expected_schema=SchemaConfigs.AUTH_SIGNUP.value.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )
        if expected_response_status != HTTPStatus.OK:
            return None
        assert mock.call_args[1]["email"] == email
        return mock.call_args[1]["token"]

    def validate_email(
        self,
        token: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        return self.post(
            endpoint="/api/auth/validate-email",
            headers=get_authorization_header(scheme="Bearer", token=token),
            expected_schema=SchemaConfigs.AUTH_VALIDATE_EMAIL.value.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def resend_validation_email(
        self,
        email: str,
        mocker,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        mock = mocker.patch("middleware.primary_resource_logic.signup.send_signup_link")
        self.post(
            endpoint="/api/auth/resend-validation-email",
            json={"email": email},
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )
        if not expected_response_status == HTTPStatus.OK:
            return None
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
        record_categories: Optional[list[RecordCategories]] = None,
        record_types: Optional[list[RecordTypes]] = None,
        format: Optional[OutputFormatEnum] = OutputFormatEnum.JSON,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema: Optional[
            Union[Type[Schema], Schema]
        ] = SchemaConfigs.SEARCH_LOCATION_AND_RECORD_TYPE_GET.value.primary_output_schema,
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
            last_archived_before = last_archived_before.strftime("%Y-%m-%d")

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
            expected_schema=SchemaConfigs.ARCHIVES_GET.value.primary_output_schema,
            headers=headers,
        )

    def federal_search(
        self,
        headers: dict,
        page: int = 1,
        record_categories: Optional[list[RecordCategories]] = None,
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
            expected_schema=SchemaConfigs.SEARCH_FEDERAL_GET.value.primary_output_schema,
        )

    @staticmethod
    def _get_search_query_params(
        record_categories: Optional[list[RecordCategories]],
        location_id: int,
        record_types: Optional[list[RecordTypes]] = None,
    ):
        query_params = {
            "location_id": location_id,
        }
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

    def follow_search(
        self,
        headers: dict,
        location_id: int,
        record_categories: Optional[list[RecordCategories]] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        endpoint_base = "/api/search/follow"
        query_params = self._get_search_query_params(
            location_id=location_id,
            record_categories=record_categories,
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
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_POST.value.primary_output_schema,
        )

    def get_user_by_id(
        self,
        headers: dict,
        user_id: int,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=SchemaConfigs.USER_PROFILE_GET.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.DATA_REQUESTS_GET_MANY.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.DATA_REQUESTS_BY_ID_WITHDRAW.value.primary_output_schema,
        )

    def get_data_request_by_id(
        self,
        data_request_id: int,
        headers: dict,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=SchemaConfigs.DATA_REQUESTS_BY_ID_GET.value.primary_output_schema,
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
        expected_schema=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_DELETE.value.primary_output_schema,
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
        expected_schema=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_DELETE.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.USER_PROFILE_DATA_REQUESTS_GET.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.AGENCIES_GET_MANY.value.primary_output_schema,
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
            endpoint=f"/api/user/update-password",
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

    @dataclass
    class BulkOperationParams:
        file: BytesIO
        headers: dict
        expected_response_status: HTTPStatus = HTTPStatus.OK

    def insert_agencies_bulk(
        self,
        bop: BulkOperationParams,
        expected_schema=SchemaConfigs.BULK_AGENCIES_POST.value.primary_output_schema,
    ):
        return self.post(
            endpoint="/api/bulk/agencies",
            headers=bop.headers,
            file=bop.file,
            expected_schema=expected_schema,
            expected_response_status=bop.expected_response_status,
        )

    def insert_data_sources_bulk(
        self,
        bop: BulkOperationParams,
        expected_schema=SchemaConfigs.BULK_DATA_SOURCES_POST.value.primary_output_schema,
    ):
        return self.post(
            endpoint="/api/bulk/data-sources",
            headers=bop.headers,
            file=bop.file,
            expected_schema=expected_schema,
            expected_response_status=bop.expected_response_status,
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
            expected_schema=SchemaConfigs.DATA_SOURCES_GET_MANY.value.primary_output_schema,
        )

    def get_agency_by_id(self, headers: dict, id: int):
        return self.get(
            endpoint=f"/api/agencies/{id}",
            headers=headers,
            expected_schema=SchemaConfigs.AGENCIES_BY_ID_GET.value.primary_output_schema,
        )

    def get_data_source_by_id(self, headers: dict, id: int):
        return self.get(
            endpoint=f"/api/data-sources/{id}",
            headers=headers,
            expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.MATCH_AGENCY.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.LOCATIONS_BY_ID_GET.value.primary_output_schema,
        )

    def get_location_related_data_requests(
        self,
        headers: dict,
        location_id: int,
    ):
        return self.get(
            endpoint=f"/api/locations/{location_id}/data-requests",
            headers=headers,
            expected_schema=SchemaConfigs.LOCATIONS_RELATED_DATA_REQUESTS_GET.value.primary_output_schema,
        )

    def get_metrics(
        self,
        headers: dict,
    ):
        return self.get(
            endpoint=f"/api/metrics",
            headers=headers,
            expected_schema=SchemaConfigs.METRICS_GET.value.primary_output_schema,
        )

    def get_user_by_id_admin(self, headers: dict, user_id: str):
        return self.get(
            endpoint=f"/api/admin/users/{user_id}",
            headers=headers,
            expected_schema=SchemaConfigs.ADMIN_USERS_BY_ID_GET.value.primary_output_schema,
        )

    def get_users(self, headers: dict, page: int = 1):
        return self.get(
            endpoint=f"/api/admin/users?page={page}",
            headers=headers,
            expected_schema=SchemaConfigs.ADMIN_USERS_GET_MANY.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.ADMIN_USERS_POST.value.primary_output_schema,
        )

    def delete_user(self, headers: dict, user_id: str):
        return self.delete(
            endpoint=f"/api/admin/users/{user_id}",
            headers=headers,
            expected_schema=SchemaConfigs.ADMIN_USERS_BY_ID_DELETE.value.primary_output_schema,
        )

    def update_admin_user(self, headers: dict, resource_id: str, password: str):
        return self.put(
            endpoint=f"/api/admin/users/{resource_id}",
            headers=headers,
            json={"password": password},
            expected_schema=SchemaConfigs.ADMIN_USERS_BY_ID_PUT.value.primary_output_schema,
        )

    def get_record_types_and_categories(self, headers: dict):
        return self.get(
            endpoint="/api/metadata/record-types-and-categories",
            headers=headers,
            expected_schema=SchemaConfigs.RECORD_TYPE_AND_CATEGORY_GET.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST.value.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def typeahead_agency(self, query: str):
        return self.get(
            endpoint=f"/api/typeahead/agencies?query={query}",
            expected_schema=SchemaConfigs.TYPEAHEAD_AGENCIES.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.PROPOSAL_AGENCIES_POST.value.primary_output_schema,
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
        expected_schema: Schema = SchemaConfigs.DATA_SOURCES_BY_ID_REJECT.value.primary_output_schema,
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
        expected_schema: Schema = SchemaConfigs.SOURCE_COLLECTOR_DATA_SOURCES_POST.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.LOCATIONS_BY_ID_PUT.value.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )

    def get_locations_map(
        self, headers: dict, expected_json_content: Optional[dict] = None
    ):
        return self.get(
            endpoint="/api/map/locations",
            headers=headers,
            expected_schema=SchemaConfigs.LOCATIONS_MAP.value.primary_output_schema,
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
            expected_schema=SchemaConfigs.LOCATIONS_GET_MANY.value.primary_output_schema,
            expected_json_content=expected_json_content,
        )

    def get_metrics_followed_searches_breakdown(
        self, headers: dict, dto: MetricsFollowedSearchesBreakdownRequestDTO
    ):
        return self.get(
            endpoint="/api/metrics/followed-searches/breakdown",
            headers=headers,
            query_parameters=dto.model_dump(mode="json"),
            expected_schema=SchemaConfigs.METRICS_FOLLOWED_SEARCHES_BREAKDOWN_GET.value.primary_output_schema,
        )

    def get_metrics_followed_searches_aggregate(self, headers: dict):
        return self.get(
            endpoint="/api/metrics/followed-searches/aggregate",
            headers=headers,
            expected_schema=SchemaConfigs.METRICS_FOLLOWED_SEARCHES_AGGREGATE_GET.value.primary_output_schema,
        )

    def post_source_collector_duplicates(self, headers: dict, urls: List[str]):
        return self.post(
            endpoint="/api/source-collector/data-sources/duplicates",
            headers=headers,
            json={"urls": urls},
            expected_schema=SchemaConfigs.SOURCE_COLLECTOR_DUPLICATES_POST.value.primary_output_schema,
        )
