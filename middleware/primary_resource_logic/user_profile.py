from http import HTTPStatus

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RelationRoleEnum
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import format_list_response
from middleware.enums import PermissionsEnum
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_with_permitted_columns,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


def get_owner_data_requests_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetManyBaseDTO
):
    user_id = access_info.get_user_id()
    data_requests = get_owner_data_requests(db_client, dto, user_id)
    formatted_list_response = format_list_response(data_requests)

    return FlaskResponseManager.make_response(formatted_list_response)


def get_owner_data_requests(
    db_client: DatabaseClient, dto: GetManyBaseDTO, user_id: int
):
    data_requests = get_data_requests_with_permitted_columns(
        db_client=db_client,
        relation_role=RelationRoleEnum.OWNER,
        dto=dto,
        where_mappings=WhereMapping.from_dict({"creator_user_id": user_id}),
        build_metadata=True,
    )
    return data_requests


def get_user_recent_searches(db_client: DatabaseClient, access_info: AccessInfoPrimary):
    recent_searches = db_client.get_user_recent_searches(
        user_id=access_info.get_user_id()
    )

    return FlaskResponseManager.make_response(recent_searches)


def get_user_by_id_wrapper(
    db_client: DatabaseClient, user_id: int, access_info: AccessInfoPrimary
):
    # Check that user is either owner or admin
    if (
        user_id != access_info.get_user_id()
        and PermissionsEnum.READ_ALL_USER_INFO not in access_info.permissions
    ):
        return FlaskResponseManager.make_response(
            data={"message": "Forbidden."}, status_code=HTTPStatus.FORBIDDEN
        )

    # Get user info
    email = db_client.get_user_email(user_id=user_id)
    external_accounts = db_client.get_user_external_accounts(user_id=user_id)
    recent_searches = db_client.get_user_recent_searches(user_id=user_id)
    followed_searches = db_client.get_user_followed_searches(left_id=user_id)
    data_requests = get_owner_data_requests(
        db_client=db_client, dto=GetManyBaseDTO(page=1), user_id=user_id
    )
    permissions = db_client.get_user_permissions(user_id)
    data = {
        "email": email,
        "external_accounts": external_accounts,
        "recent_searches": recent_searches,
        "followed_searches": followed_searches,
        "data_requests": data_requests,
        "permissions": [permission.value for permission in permissions],
    }
    json_body = {"data": data}

    return FlaskResponseManager.make_response(data=json_body)
