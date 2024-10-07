from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import make_response, Response
from marshmallow import fields

from database_client.db_client_dataclasses import WhereMapping, OrderByParameters
from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum, RelationRoleEnum
from database_client.subquery_logic import SubqueryParameterManager
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import (
    get_permitted_columns,
    RelationRoleParameters,
)
from middleware.custom_dataclasses import (
    DeferredFunction,
)
from middleware.dynamic_request_logic.common_functions import check_for_id
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry, PostLogic
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetByIDBaseDTO,
    GetByIDBaseSchema,
    GetManyBaseDTO,
)
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations

from middleware.common_response_formatting import (
    multiple_results_response,
    message_response,
)
from utilities.enums import SourceMappingEnum

RELATION = Relations.DATA_REQUESTS.value
RELATED_SOURCES_RELATION = Relations.RELATED_SOURCES.value

DATA_REQUESTS_SUBQUERY_PARAMS = [SubqueryParameterManager.data_sources()]

class RelatedSourceByIDSchema(GetByIDBaseSchema):
    data_source_id = fields.Str(
        required=True,
        metadata={
            "description": "The ID of the data source",
            "source": SourceMappingEnum.PATH,
        },
    )


@dataclass
class RelatedSourceByIDDTO(GetByIDBaseDTO):
    data_source_id: int

    def get_where_mapping(self):
        return {"source_id": self.data_source_id, "request_id": self.resource_id}


def get_data_requests_relation_role(
    db_client: DatabaseClient, data_request_id: Optional[int], access_info: AccessInfo
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
    user_id = db_client.get_user_id(access_info.user_email)
    if db_client.user_is_creator_of_data_request(
        user_id=user_id, data_request_id=data_request_id
    ):
        return RelationRoleEnum.OWNER
    return RelationRoleEnum.STANDARD


def add_creator_user_id(
    db_client: DatabaseClient, user_email: str, dto: EntryDataRequestDTO
):
    user_id = db_client.get_user_id(user_email)
    dto.entry_data.update({"creator_user_id": user_id})


def create_data_request_wrapper(
    db_client: DatabaseClient, dto: EntryDataRequestDTO, access_info: AccessInfo
) -> Response:
    """
    Create a data request
    :param db_client:
    :param access_info:
    :param data_request_data:
    :return:
    """
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.create_data_request,
        ),
        entry=dto.entry_data,
        pre_insertion_function_with_parameters=DeferredFunction(
            function=add_creator_user_id,
            db_client=db_client,
            user_email=access_info.user_email,
            dto=dto,
        ),
        relation_role_parameters=RelationRoleParameters(
            relation_role_override=RelationRoleEnum.OWNER
        ),
    )


def get_data_requests_wrapper(
    db_client: DatabaseClient, dto: GetManyBaseDTO, access_info: AccessInfo
) -> Response:
    """
    Get data requests
    :param dto:
    :param db_client:
    :param access_info:
    :return:
    """
    return get_many(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="data requests",
            relation=RELATION,
            db_client_method=DatabaseClient.get_data_requests,
            subquery_parameters=DATA_REQUESTS_SUBQUERY_PARAMS
        ),
        page=dto.page,
    )


def get_data_requests_with_permitted_columns(
    db_client,
    relation_role,
    dto: GetManyBaseDTO,
    where_mappings: Optional[list[WhereMapping]] = [True],
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
        subquery_parameters=DATA_REQUESTS_SUBQUERY_PARAMS

    )
    return data_requests


def allowed_to_delete_request(access_info, data_request_id, db_client):
    user_id = db_client.get_user_id(email=access_info.user_email)
    return (
        db_client.user_is_creator_of_data_request(
            user_id=user_id, data_request_id=data_request_id
        )
        or PermissionsEnum.DB_WRITE in access_info.permissions
    )


def delete_data_request_wrapper(
    db_client: DatabaseClient, data_request_id: int, access_info: AccessInfo
) -> Response:
    """
    Delete data requests
    :param db_client:
    :param access_info:
    :return:
    """
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.delete_data_request,
        ),
        id_info=IDInfo(id_column_value=data_request_id),
        permission_checking_function=DeferredFunction(
            allowed_to_delete_request,
            access_info=access_info,
            data_request_id=data_request_id,
            db_client=db_client,
        ),
    )


def update_data_request_wrapper(
    db_client: DatabaseClient,
    dto: EntryDataRequestDTO,
    data_request_id: int,
    access_info: AccessInfo,
):
    """
    Update data requests
    :param db_client:
    :param access_info:
    :return:
    """
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.update_data_request,
        ),
        entry=dto.entry_data,
        entry_id=data_request_id,
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=data_request_id,
                db_client=db_client,
            )
        ),
    )


def get_data_request_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetByIDBaseDTO
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
            relation=RELATION,
            access_info=access_info,
            db_client_method=DatabaseClient.get_data_requests,
            entry_name="Data request",
            subquery_parameters=DATA_REQUESTS_SUBQUERY_PARAMS
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
    # TODO: Generalize for other related source-getting.
    check_for_id(
        db_client=db_client,
        table_name=RELATION,
        id_info=IDInfo(id_column_value=int(dto.resource_id)),
    )
    permitted_columns = get_permitted_columns(
        db_client=db_client,
        relation=Relations.DATA_SOURCES_EXPANDED.value,
        role=RelationRoleEnum.STANDARD,
        column_permission=ColumnPermissionEnum.READ,
    )
    results = db_client.get_linked_rows(
        link_table=Relations.LINK_DATA_SOURCES_DATA_REQUESTS,
        left_id=int(dto.resource_id),
        left_link_column="request_id",
        right_link_column="source_id",
        linked_relation=Relations.DATA_SOURCES_EXPANDED,
        linked_relation_linking_column="airtable_uid",
        columns_to_retrieve=permitted_columns
    )
    results.update({
        "message": "Related sources found.",
    })
    return FlaskResponseManager.make_response(data=results)


def check_can_create_data_request_related_source(relation_role: RelationRoleEnum):
    if relation_role not in [RelationRoleEnum.OWNER, RelationRoleEnum.ADMIN]:
        FlaskResponseManager.abort(
            code=HTTPStatus.FORBIDDEN,
            message="User does not have permission to perform this action.",
        )


class CreateDataRequestRelatedSourceLogic(PostLogic):

    def check_for_permission(self, relation_role: RelationRoleEnum):
        check_can_create_data_request_related_source(relation_role)

    def make_response(self) -> Response:
        return message_response("Data source successfully associated with request.")


def create_data_request_related_source(
    db_client: DatabaseClient, access_info: AccessInfo, dto: RelatedSourceByIDDTO
):
    post_logic = CreateDataRequestRelatedSourceLogic(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
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
    db_client: DatabaseClient, access_info: AccessInfo, dto: RelatedSourceByIDDTO
):
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Request-Source association",
            relation=RELATED_SOURCES_RELATION,
            db_client_method=DatabaseClient.delete_request_source_relation,
        ),
        id_info=IDInfo(
            additional_where_mappings=dto.get_where_mapping(),
        ),
        permission_checking_function=DeferredFunction(
            allowed_to_delete_request,
            access_info=access_info,
            data_request_id=dto.resource_id,
            db_client=db_client,
        ),
    )
