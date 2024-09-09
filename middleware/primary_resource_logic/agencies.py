from flask import Response

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetManyBaseDTO,
    GetByIDBaseDTO,
)
from middleware.enums import Relations


def get_agencies(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetManyBaseDTO
) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    return get_many(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agencies",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.get_agencies,
        ),
        page=dto.page,
    )


def get_agency_by_id(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetByIDBaseDTO
) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.get_agencies,
        ),
        id=dto.resource_id,
        id_column_name="airtable_uid",
    )


def create_agency(
    db_client: DatabaseClient, dto: EntryDataRequestDTO, access_info: AccessInfo
) -> Response:
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.create_agency,
        ),
        entry=dto.entry_data,
    )


def update_agency(
    db_client: DatabaseClient,
    dto: EntryDataRequestDTO,
    access_info: AccessInfo,
    agency_id: str,
) -> Response:
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.update_agency,
        ),
        entry=dto.entry_data,
        entry_id=agency_id,
    )


def delete_agency(
    db_client: DatabaseClient, access_info: AccessInfo, agency_id: str
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.delete_agency,
        ),
        id_info=IDInfo(id_column_name="airtable_uid", id_column_value=agency_id),
    )
