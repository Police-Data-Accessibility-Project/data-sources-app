from flask import Response, request

from db.client.core import DatabaseClient
from endpoints.instantiations.agencies_.put.dto import AgencyInfoPutDTO
from endpoints.instantiations.agencies_.put.query import UpdateAgencyQueryBuilder
from endpoints.instantiations.agencies_.put.schemas.outer import AgenciesPutSchema
from middleware.common_response_formatting import message_response
from middleware.security.access_info.primary import AccessInfoPrimary


def update_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    agency_id: str,
) -> Response:
    AgenciesPutSchema().load(request.json)
    entry_data = AgencyInfoPutDTO(**request.json.get("agency_info"))

    db_client.run_query_builder(
        query_builder=UpdateAgencyQueryBuilder(
            dto=entry_data,
            agency_id=int(agency_id),
        )
    )

    return message_response(message="Agency updated.")
