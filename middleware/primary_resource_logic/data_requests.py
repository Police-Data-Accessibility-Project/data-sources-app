from http import HTTPStatus
from typing import Optional

from flask import Response

from database_client.db_client_dataclasses import WhereMapping, OrderByParameters
from database_client.database_client import DatabaseClient
from database_client.enums import (
    ColumnPermissionEnum,
    RelationRoleEnum,
    RequestStatus,
)
from database_client.subquery_logic import SubqueryParameterManager, SubqueryParameters
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import (
    get_permitted_columns,
    RelationRoleParameters,
)
from middleware.custom_dataclasses import (
    DeferredFunction,
)
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.get_related_resource_logic import (
    get_related_resource,
    GetRelatedResourcesParameters,
)
from middleware.dynamic_request_logic.post_logic import PostLogic
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.location_logic import InvalidLocationError
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseDTO,
    GetManyBaseDTO,
)
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations

from middleware.common_response_formatting import (
    message_response,
    created_id_response,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    GetManyDataRequestsRequestsDTO,
    DataRequestsPutDTO,
    DataRequestsPutOuterDTO,
    RelatedSourceByIDDTO,
    RelatedLocationsByIDDTO,
    DataRequestsPostDTO,
    DataRequestLocationInfoPostDTO,
)
from middleware.util import dataclass_to_filtered_dict

RELATION = Relations.DATA_REQUESTS.value
RELATED_SOURCES_RELATION = Relations.RELATED_SOURCES.value


def get_data_requests_subquery_params() -> list[SubqueryParameters]:
    return [
        SubqueryParameterManager.data_sources(),
        SubqueryParameterManager.locations(),
    ]


def get_location_id_for_data_requests(
    db_client: DatabaseClient, location_info: DataRequestLocationInfoPostDTO
) -> int:
    """
    Get the location id for the data request
    :param db_client:
    :param location_info:
    :return:
    """
    # Rename keys to match where mappings
    revised_location_info = {
        "type": location_info.type,
        "state_name": location_info.state_name,
        "county_name": location_info.county_name,
        "locality_name": location_info.locality_name,
    }

    location_id = db_client.get_location_id(
        where_mappings=WhereMapping.from_dict(revised_location_info)
    )
    if location_id is None:
        raise InvalidLocationError()
    return location_id


def get_data_requests_relation_role(
    db_client: DatabaseClient,
    data_request_id: Optional[int],
    access_info: AccessInfoPrimary,
) -> RelationRoleEnum:
    """
    Determine the relation role for information on a data request
    :param db_client:
    :param data_request_id:
    :param access_info:
    :return:
    """
    if access_info.access_type == AccessTypeEnum.API_KEY:
        return RelationRoleEnum.STANDARD
    if PermissionsEnum.DB_WRITE in access_info.permissions:
        return RelationRoleEnum.ADMIN
    if data_request_id is None:
        return RelationRoleEnum.STANDARD

    # Check ownership
    user_id = access_info.get_user_id()
    if db_client.user_is_creator_of_data_request(
        user_id=user_id, data_request_id=data_request_id
    ):
        return RelationRoleEnum.OWNER
    return RelationRoleEnum.STANDARD


def create_data_request_wrapper(
    db_client: DatabaseClient, dto: DataRequestsPostDTO, access_info: AccessInfoPrimary
) -> Response:
    """
    Create a data request
    :param db_client:
    :param access_info:
    :param data_request_data:
    :return:
    """
    # Check that location ids are valid, and get location ids for linking
    location_ids = dto.location_ids if dto.location_ids is not None else []

    column_value_mappings_raw = dict(dto.request_info)
    user_id = access_info.get_user_id()
    column_value_mappings_raw["creator_user_id"] = user_id

    # Insert the data request, get data request id
    dr_id = db_client.create_data_request(
        column_value_mappings=column_value_mappings_raw, column_to_return="id"
    )

    # Insert location ids into linking table
    for location_id in location_ids:
        db_client.create_request_location_relation(
            column_value_mappings={"data_request_id": dr_id, "location_id": location_id}
        )

    # Return data request id
    return created_id_response(new_id=str(dr_id), message=f"Data request created.")


def _get_location_ids(db_client, dto: DataRequestsPostDTO):
    location_ids = []
    if dto.location_ids is None:
        return location_ids
    for location_info in dto.location_ids:
        try:
            location_id = get_location_id_for_data_requests(
                db_client=db_client, location_info=location_info
            )
        except InvalidLocationError:
            FlaskResponseManager.abort(
                code=HTTPStatus.BAD_REQUEST,
                message=f"Invalid location: {location_info}",
            )

        location_ids.append(location_id)
    return location_ids


def get_data_requests_wrapper(
    db_client: DatabaseClient,
    dto: GetManyDataRequestsRequestsDTO,
    access_info: AccessInfoPrimary,
) -> Response:
    """
    Get data requests
    :param dto:
    :param db_client:
    :param access_info:
    :return:
    """
    db_client_additional_args = {
        "build_metadata": True,
        "order_by": OrderByParameters.construct_from_args(
            sort_by=dto.sort_by, sort_order=dto.sort_order
        ),
        "limit": dto.limit,
    }

    if dto.request_statuses is not None:
        db_client_additional_args["where_mappings"] = {
            "request_status": [rs.value for rs in dto.request_statuses]
        }
    return get_many(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="data requests",
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            db_client_method=DatabaseClient.get_data_requests,
            subquery_parameters=get_data_requests_subquery_params(),
            db_client_additional_args=db_client_additional_args,
        ),
        page=dto.page,
    )


def get_data_requests_with_permitted_columns(
    db_client,
    relation_role,
    dto: GetManyBaseDTO,
    where_mappings: Optional[list[WhereMapping]] = [True],
    build_metadata: Optional[bool] = False,
) -> list[dict]:

    columns = get_permitted_columns(
        db_client=db_client,
        relation=RELATION,
        role=relation_role,
        column_permission=ColumnPermissionEnum.READ,
    )
    data_requests = db_client.get_data_requests(
        columns=columns,
        where_mappings=where_mappings,
        order_by=OrderByParameters.construct_from_args(dto.sort_by, dto.sort_order),
        subquery_parameters=get_data_requests_subquery_params(),
        build_metadata=build_metadata,
        limit=dto.limit,
    )
    return data_requests


def is_creator_or_admin(access_info, data_request_id, db_client):
    user_id = access_info.get_user_id()
    return (
        db_client.user_is_creator_of_data_request(
            user_id=user_id, data_request_id=data_request_id
        )
        or PermissionsEnum.DB_WRITE in access_info.permissions
    )


def delete_data_request_wrapper(
    db_client: DatabaseClient, data_request_id: int, access_info: AccessInfoPrimary
) -> Response:
    """
    Delete data requests
    :param db_client:
    :param access_info:
    :return:
    """
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.delete_data_request,
        ),
        id_info=IDInfo(id_column_value=data_request_id),
        permission_checking_function=DeferredFunction(
            is_creator_or_admin,
            access_info=access_info,
            data_request_id=data_request_id,
            db_client=db_client,
        ),
    )


def optionally_update_github_issue_info(
    db_client: DatabaseClient, entry_data: DataRequestsPutDTO, data_request_id: int
):
    d = {}
    if entry_data.github_issue_url is not None:
        d["github_issue_url"] = entry_data.github_issue_url
    if entry_data.github_issue_number is not None:
        d["github_issue_number"] = entry_data.github_issue_number
    if len(d) > 0:
        db_client._update_entry_in_table(
            table_name=Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value,
            entry_id=data_request_id,
            id_column_name="data_request_id",
            column_edit_mappings=d,
        )


def update_data_request_wrapper(
    db_client: DatabaseClient,
    dto: DataRequestsPutOuterDTO,
    data_request_id: int,
    access_info: AccessInfoPrimary,
):
    """
    Update data requests
    :param db_client:
    :param access_info:
    :return:
    """
    entry_dict = created_filtered_entry_dict(dto)
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.update_data_request,
        ),
        entry=entry_dict,
        entry_id=data_request_id,
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=data_request_id,
                db_client=db_client,
            )
        ),
        pre_update_method_with_parameters=DeferredFunction(
            function=optionally_update_github_issue_info,
            db_client=db_client,
            entry_data=dto.entry_data,
            data_request_id=data_request_id,
        ),
    )


def created_filtered_entry_dict(dto: DataRequestsPutOuterDTO) -> dict:
    entry_dict = dataclass_to_filtered_dict(dto.entry_data)
    if "github_issue_url" in entry_dict:
        del entry_dict["github_issue_url"]
    if "github_issue_number" in entry_dict:
        del entry_dict["github_issue_number"]
    return entry_dict


def get_data_request_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:
    """
    Get data requests
    :param dto:
    :param db_client:
    :param access_info:
    :return:
    """
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            access_info=access_info,
            db_client_method=DatabaseClient.get_data_requests,
            entry_name="Data request",
            subquery_parameters=get_data_requests_subquery_params(),
        ),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=dto.resource_id,
                db_client=db_client,
            )
        ),
        id=dto.resource_id,
    )


def get_data_request_related_sources(db_client: DatabaseClient, dto: GetByIDBaseDTO):

    return get_related_resource(
        get_related_resources_parameters=GetRelatedResourcesParameters(
            dto=dto,
            db_client_method=DatabaseClient.get_data_requests,
            primary_relation=Relations.DATA_REQUESTS,
            related_relation=Relations.DATA_SOURCES_EXPANDED,
            linking_column="data_sources",
            metadata_count_name="data_sources_count",
            resource_name="sources",
        )
    )


def get_data_request_related_locations(
    db_client: DatabaseClient, dto: GetByIDBaseDTO
) -> Response:
    return get_related_resource(
        get_related_resources_parameters=GetRelatedResourcesParameters(
            dto=dto,
            db_client_method=DatabaseClient.get_data_requests,
            primary_relation=Relations.DATA_REQUESTS,
            related_relation=Relations.LOCATIONS_EXPANDED,
            linking_column="locations",
            metadata_count_name="locations_count",
            resource_name="locations",
        ),
        permitted_columns=[
            "id",
            "state_name",
            "state_iso",
            "county_name",
            "county_fips",
            "locality_name",
            "type",
        ],
        alias_mappings={"id": "location_id"},
    )


def check_has_admin_or_owner_role(relation_role: RelationRoleEnum):
    if relation_role not in [RelationRoleEnum.OWNER, RelationRoleEnum.ADMIN]:
        FlaskResponseManager.abort(
            code=HTTPStatus.FORBIDDEN,
            message="User does not have permission to perform this action.",
        )


class CreateDataRequestRelatedSourceLogic(PostLogic):

    def check_can_edit_columns(self, relation_role: RelationRoleEnum):
        check_has_admin_or_owner_role(relation_role)

    def make_response(self) -> Response:
        return message_response("Data source successfully associated with request.")


class CreateDataRequestRelatedLocationLogic(PostLogic):

    def check_can_edit_columns(self, relation_role: RelationRoleEnum):
        check_has_admin_or_owner_role(relation_role)

    def make_response(self) -> Response:
        return message_response("Location successfully associated with request.")


def create_data_request_related_source(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: RelatedSourceByIDDTO
):
    post_logic = CreateDataRequestRelatedSourceLogic(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Source association",
            relation=RELATED_SOURCES_RELATION,
            db_client_method=DatabaseClient.create_request_source_relation,
        ),
        entry=dto.get_where_mapping(),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=dto.resource_id,
                db_client=db_client,
            )
        ),
    )
    return post_logic.execute()


def delete_data_request_related_source(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: RelatedSourceByIDDTO
):
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Source association",
            relation=RELATED_SOURCES_RELATION,
            db_client_method=DatabaseClient.delete_request_source_relation,
        ),
        id_info=IDInfo(
            additional_where_mappings=dto.get_where_mapping(),
        ),
        permission_checking_function=DeferredFunction(
            is_creator_or_admin,
            access_info=access_info,
            data_request_id=dto.resource_id,
            db_client=db_client,
        ),
    )


def create_data_request_related_location(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedLocationsByIDDTO,
):
    post_logic = CreateDataRequestRelatedLocationLogic(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Location association",
            relation=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
            db_client_method=DatabaseClient.create_request_location_relation,
        ),
        entry=dto.get_where_mapping(),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=dto.resource_id,
                db_client=db_client,
            )
        ),
    )
    return post_logic.execute()


def delete_data_request_related_location(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedLocationsByIDDTO,
):
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Location association",
            relation=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
            db_client_method=DatabaseClient.delete_request_location_relation,
        ),
        id_info=IDInfo(
            additional_where_mappings=dto.get_where_mapping(),
        ),
        permission_checking_function=DeferredFunction(
            is_creator_or_admin,
            access_info=access_info,
            data_request_id=dto.resource_id,
            db_client=db_client,
        ),
    )


def withdraw_data_request_wrapper(
    db_client: DatabaseClient, data_request_id: int, access_info: AccessInfoPrimary
) -> Response:
    if not is_creator_or_admin(
        access_info=access_info, data_request_id=data_request_id, db_client=db_client
    ):
        FlaskResponseManager.abort(
            code=HTTPStatus.FORBIDDEN,
            message="User does not have permission to perform this action.",
        )
    db_client.update_data_request(
        entry_id=data_request_id,
        column_edit_mappings={"request_status": RequestStatus.REQUEST_WITHDRAWN.value},
    )
    return message_response("Data request successfully withdrawn.")
