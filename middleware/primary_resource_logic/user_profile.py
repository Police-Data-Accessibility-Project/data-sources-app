from flask import make_response

from db.client.core import DatabaseClient
from db.db_client_dataclasses import WhereMapping
from db.enums import RelationRoleEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import format_list_response
from middleware.primary_resource_logic.data_requests_.get.with_permitted_columns import (
    get_data_requests_with_permitted_columns,
)
from middleware.schema_and_dto.dtos.common.base import GetManyBaseDTO


def get_owner_data_requests_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetManyBaseDTO
):
    user_id = access_info.get_user_id()
    data_requests = get_owner_data_requests(db_client, dto, user_id)
    formatted_list_response = format_list_response(data_requests)

    return make_response(formatted_list_response)


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

    return make_response(recent_searches)
