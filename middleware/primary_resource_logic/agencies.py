from flask import Response, make_response

from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from db.subquery_logic import SubqueryParameterManager
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import (
    message_response,
)
from middleware.schema_and_dto.dtos.agencies.get_many import AgenciesGetManyDTO
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO

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
