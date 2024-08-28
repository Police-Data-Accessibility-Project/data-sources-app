from http import HTTPStatus
from typing import Optional

from flask import make_response, Response
from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum, RelationRoleEnum
from middleware.access_logic import AccessInfo, get_access_info_from_jwt
from middleware.column_permission_logic import get_permitted_columns, check_has_permission_to_edit_columns, \
    RelationRoleParameters
from middleware.custom_dataclasses import EntryDataRequest, MiddlewareParameters, PostParameters, DeferredFunction
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations
from middleware.get_by_id_logic import get_by_id, post_entry
from middleware.util import message_response, format_list_response

RELATION = Relations.DATA_REQUESTS.value

def get_data_requests_relation_role(
    db_client: DatabaseClient, data_request_id: Optional[str], access_info: AccessInfo
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

def add_creator_user_id(db_client: DatabaseClient, user_email: str, dto: EntryDataRequest):
    user_id = db_client.get_user_id(user_email)
    dto.entry_data.update({"creator_user_id": user_id})

def create_data_request_wrapper(
        db_client: DatabaseClient,
        dto: EntryDataRequest,
        access_info: AccessInfo
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
        )
    )

def get_data_requests_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfo
) -> Response:
    """
    Get data requests
    :param db_client:
    :param access_info:
    :return:
    """

    relation_role = get_data_requests_relation_role(
        db_client,
        data_request_id=None,
        access_info=access_info
    )
    formatted_data_requests = get_formatted_data_requests(access_info, db_client, relation_role)
    formatted_list_response = format_list_response(formatted_data_requests)

    return make_response(
        formatted_list_response,
        HTTPStatus.OK,
    )


def get_formatted_data_requests(access_info, db_client, relation_role) -> list[dict]:

    if relation_role == RelationRoleEnum.ADMIN:
        return get_data_requests_with_permitted_columns(
            db_client,
            relation_role
        )
    elif relation_role == RelationRoleEnum.STANDARD:
        return get_standard_and_owner_zipped_data_requests(
            access_info.user_email,
            db_client
        )
    raise ValueError(f"Invalid relation role: {relation_role}")


def get_standard_and_owner_zipped_data_requests(user_email, db_client):
    user_id = db_client.get_user_id(user_email)
    # Create two requests -- one where the user is the creator and one where the user is not
    mapping = {"creator_user_id": user_id}
    zipped_standard_requests = get_data_requests_with_permitted_columns(
        db_client=db_client,
        relation_role=RelationRoleEnum.STANDARD,
        not_where_mappings=mapping
    )
    zipped_owner_requests = get_data_requests_with_permitted_columns(
        db_client=db_client,
        relation_role=RelationRoleEnum.OWNER,
        where_mappings=mapping
    )
    # Combine these so that the owner requests are listed first
    zipped_data_requests = zipped_owner_requests + zipped_standard_requests
    return zipped_data_requests


def get_data_requests_with_permitted_columns(
        db_client,
        relation_role,
        where_mappings: Optional[dict] = None,
        not_where_mappings: Optional[dict] = None
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
        not_where_mappings=not_where_mappings
    )
    return data_requests


def delete_data_request_wrapper(
    db_client: DatabaseClient,
    data_request_id: int,
    access_info: AccessInfo
) -> Response:
    """
    Delete data requests
    :param db_client:
    :param access_info:
    :return:
    """
    check_if_allowed_to_delete_data_request(access_info, data_request_id, db_client)
    return delete_data_request(data_request_id, db_client)


def delete_data_request(data_request_id, db_client):
    db_client.delete_data_request(
        id_column_value=data_request_id)
    return message_response(
        "Data request deleted",
        HTTPStatus.OK,
    )


def check_if_allowed_to_delete_data_request(access_info, data_request_id, db_client):
    if not allowed_to_delete_request(access_info, data_request_id, db_client):
        abort(
            code=HTTPStatus.FORBIDDEN,
            message="You do not have permission to delete this data request",
        )


def allowed_to_delete_request(access_info, data_request_id, db_client):
    user_id = db_client.get_user_id(access_info.user_email)
    return db_client.user_is_creator_of_data_request(
        user_id=user_id,
        data_request_id=data_request_id
    ) or PermissionsEnum.DB_WRITE in access_info.permissions


def update_data_request_wrapper(
    db_client: DatabaseClient,
    dto: EntryDataRequest,
    data_request_id: str,
    access_info: AccessInfo
):
    """
    Update data requests
    :param db_client:
    :param access_info:
    :return:
    """
    relation_role = get_data_requests_relation_role(db_client, data_request_id, access_info)
    check_has_permission_to_edit_columns(
        db_client=db_client,
        relation=RELATION,
        role=relation_role,
        columns=list(dto.entry_data.keys())
    )
    db_client.update_data_request(
        column_edit_mappings=dto.entry_data,
        entry_id=data_request_id
    )
    return message_response(
        "Data request updated",
        HTTPStatus.OK,
    )

def get_data_request_by_id_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    data_request_id: str
) -> Response:
    """
    Get data requests
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
            entry_name="Data request"
        ),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=data_request_id,
                db_client=db_client
            )
        ),
        id=data_request_id,
    )