from flask import Response, request, make_response

from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from db.subquery_logic import SubqueryParameterManager
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import (
    created_id_response,
    message_response,
)
from middleware.dynamic_request_logic.delete import delete_entry
from middleware.dynamic_request_logic.post import PostHandler
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
    PutPostRequestInfo,
)
from middleware.schema_and_dto.schemas.agencies.put import AgenciesPutSchema
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO
from middleware.schema_and_dto.dtos.agencies.get_many import AgenciesGetManyDTO
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.enums import Relations

SUBQUERY_PARAMS = [SubqueryParameterManager.data_sources()]


def get_agencies(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: AgenciesGetManyDTO
) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :param dto: The AgenciesGetManyDTO object.
    :return: A response object with the relevant agency information and status code.
    """

    results = db_client.get_agencies(
        order_by=OrderByParameters.construct_from_args(
            sort_by=dto.sort_by, sort_order=dto.sort_order
        ),
        page=dto.page,
        limit=dto.limit,
        requested_columns=dto.requested_columns,
        approval_status=dto.approval_status,
    )

    return make_response(
        {
            "metadata": {"count": len(results)},
            "message": "Successfully retrieved agencies",
            "data": results,
        }
    )


def get_agency_by_id(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:
    result = db_client.get_agency_by_id(int(dto.resource_id))

    if result is None:
        return message_response(message="No such agency exists")
    else:
        return message_response(message="Successfully retrieved agency", data=result)


def validate_and_add_location_info(
    db_client: DatabaseClient, entry_data: dict, location_id: int
):
    """
    Checks that location provided is a valid one, and returns the associated location id
    In the case of a locality which does not yet exist, adds it and returns the location id
    :param db_client:
    :param entry_data: Modified in-place
    :param location_id:
    :return:
    """
    entry_data["location_id"] = location_id


class AgencyPostRequestInfo(PutPostRequestInfo):
    dto: AgenciesPostDTO


class AgencyPostHandler(PostHandler):
    def __init__(self):
        super().__init__(middleware_parameters=AGENCY_POST_MIDDLEWARE_PARAMETERS)

    def pre_execute(self, request: AgencyPostRequestInfo):
        validate_and_add_location_info(
            db_client=DatabaseClient(),
            entry_data=request.entry,
            location_id=request.dto.location_ids,
        )


AGENCY_POST_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="agency",
    relation=Relations.AGENCIES.value,
    db_client_method=DatabaseClient.create_agency,
)


def create_agency(
    db_client: DatabaseClient,
    dto: AgenciesPostDTO,
    access_info: AccessInfoPrimary,
) -> Response:
    agency_id = db_client.create_agency(dto, user_id=access_info.user_id)

    return created_id_response(new_id=str(agency_id), message="Agency created.")


AGENCY_PUT_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="agency",
    relation=Relations.AGENCIES.value,
    db_client_method=DatabaseClient.update_agency,
)


def update_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    agency_id: str,
) -> Response:
    AgenciesPutSchema().load(request.json)
    entry_data = request.json.get("agency_info")

    db_client.update_agency(
        entry_id=int(agency_id),
        column_edit_mappings=entry_data,
    )

    return message_response(message="Agency updated.")


def delete_agency(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, agency_id: str
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.delete_agency,
        ),
        id_info=IDInfo(id_column_value=int(agency_id)),
    )


def add_agency_related_location(
    db_client: DatabaseClient, agency_id: int, location_id: int
) -> Response:
    db_client.add_location_to_agency(agency_id=agency_id, location_id=location_id)
    return message_response(message="Location added to agency.")


def remove_agency_related_location(
    db_client: DatabaseClient, agency_id: int, location_id: int
) -> Response:
    db_client.remove_location_from_agency(agency_id=agency_id, location_id=location_id)
    return message_response(message="Location removed from agency.")
