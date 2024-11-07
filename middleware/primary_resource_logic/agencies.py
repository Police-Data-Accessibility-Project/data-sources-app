from dataclasses import asdict

from flask import Response, request

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.location_logic import get_location_id
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import (
    AgenciesPutSchema,
    AgenciesPostDTO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    GetByIDBaseDTO,
    LocationInfoDTO,
)
from middleware.enums import Relations, JurisdictionType


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
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
            db_client_additional_args={"build_metadata": True},
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
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
        ),
        id=dto.resource_id,
    )


def validate_and_add_location_info(
    db_client: DatabaseClient, entry_data: dict, location_info: LocationInfoDTO
):
    """
    Checks that location provided is a valid one, and returns the associated location id
    In the case of a locality which does not yet exist, adds it and returns the location id
    :param db_client:
    :param entry_data: Modified in-place
    :param location_info:
    :return:
    """
    location_id = get_location_id(db_client, location_info)
    entry_data["location_id"] = location_id


def create_agency(
    db_client: DatabaseClient, dto: AgenciesPostDTO, access_info: AccessInfo
) -> Response:
    entry_data = asdict(dto.agency_info)
    deferred_function = optionally_get_location_info_deferred_function(
        db_client=db_client,
        jurisdiction_type=dto.agency_info.jurisdiction_type,
        entry_data=entry_data,
        location_info=dto.location_info,
    )

    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.create_agency,
        ),
        entry=entry_data,
        pre_insertion_function_with_parameters=deferred_function,
    )


def optionally_get_location_info_deferred_function(
    db_client: DatabaseClient,
    jurisdiction_type: JurisdictionType,
    entry_data: dict,
    location_info: LocationInfoDTO,
):
    if jurisdiction_type == JurisdictionType.FEDERAL:
        deferred_function = None
    else:
        deferred_function = DeferredFunction(
            function=validate_and_add_location_info,
            db_client=db_client,
            entry_data=entry_data,
            location_info=location_info,
        )
    return deferred_function


def update_agency(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    agency_id: str,
) -> Response:
    AgenciesPutSchema().load(request.json)
    entry_data = request.json.get("agency_info")
    location_info = request.json.get("location_info")
    if location_info is not None:
        jurisdiction_type = entry_data.get("jurisdiction_type")
        deferred_function = optionally_get_location_info_deferred_function(
            db_client=db_client,
            jurisdiction_type=jurisdiction_type,
            entry_data=entry_data,
            location_info=location_info,
        )
    else:
        deferred_function = None

    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.update_agency,
        ),
        entry=entry_data,
        entry_id=int(agency_id),
        pre_update_method_with_parameters=deferred_function,
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
        id_info=IDInfo(id_column_value=int(agency_id)),
    )
