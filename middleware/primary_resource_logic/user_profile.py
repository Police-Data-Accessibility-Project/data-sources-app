from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.common_response_formatting import format_list_response
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_with_permitted_columns,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


def get_owner_data_requests_wrapper(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetManyBaseDTO
):
    user_id = db_client.get_user_id(access_info.user_email)
    data_requests = get_data_requests_with_permitted_columns(
        db_client=db_client,
        relation_role=RelationRoleEnum.OWNER,
        dto=dto,
        where_mappings=WhereMapping.from_dict({"creator_user_id": user_id}),
    )
    formatted_list_response = format_list_response(data_requests)

    return FlaskResponseManager.make_response(formatted_list_response)
