from enum import Enum
from typing import Optional, List

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_dtos.match_dtos import (
    AgencyMatchOuterDTO,
    AgencyMatchDTO,
)
from rapidfuzz import fuzz

from middleware.util import update_if_not_none


class AgencyMatchStatus(Enum):
    EXACT = "Exact Match"
    PARTIAL = "Partial Matches"
    NO_MATCH = "No Match"


SIMILARITY_THRESHOLD = 80


def get_agency_match_message(status: AgencyMatchStatus):
    match status:
        case AgencyMatchStatus.EXACT:
            return "Exact match found."
        case AgencyMatchStatus.PARTIAL:
            return "Partial matches found."
        case AgencyMatchStatus.NO_MATCH:
            return "No matches found."


class AgencyMatchResponse:

    def __init__(self, status: AgencyMatchStatus, agencies: Optional[list] = None):
        self.status = status
        self.agencies = agencies
        self.message = get_agency_match_message(status)


def match_agencies(db_client: DatabaseClient, dto: AgencyMatchOuterDTO):
    amrs: List[AgencyMatchResponse] = []
    for entry in dto.entries:
        amr: AgencyMatchResponse = try_matching_agency(db_client=db_client, dto=entry)
        amrs.append(amr)


def try_getting_exact_match_agency(dto: AgencyMatchDTO, agencies: list[dict]):
    for agency in agencies:
        if agency["submitted_name"] == dto.name:
            return agency


def try_getting_partial_match_agencies(dto: AgencyMatchDTO, agencies: list[dict]):
    partial_matches = []
    for agency in agencies:
        if fuzz.ratio(dto.name, agency["submitted_name"]) >= SIMILARITY_THRESHOLD:
            partial_matches.append(agency)

    return partial_matches

def format_response(amr: AgencyMatchResponse) -> Response:
    data = {
        "status": amr.status.value,
        "message": amr.message,
    }
    update_if_not_none(dict_to_update=data, secondary_dict={"agencies": amr.agencies})
    return FlaskResponseManager.make_response(
        data=data,
    )

def match_agency_wrapper(db_client: DatabaseClient, dto: AgencyMatchOuterDTO):
    result = try_matching_agency(db_client=db_client, dto=dto)
    return format_response(result)


def try_matching_agency(
    db_client: DatabaseClient, dto: AgencyMatchDTO
) -> AgencyMatchResponse:

    location_id = _get_location_id(db_client, dto)
    if location_id is None:
        return _no_match_response()

    agencies = _get_agencies(db_client, location_id)
    if len(agencies) == 0:
        return _no_match_response()

    exact_match_agency = try_getting_exact_match_agency(dto=dto, agencies=agencies)
    if exact_match_agency is not None:
        return _exact_match_response(exact_match_agency)

    partial_match_agencies = try_getting_partial_match_agencies(
        dto=dto, agencies=agencies
    )
    if len(partial_match_agencies) > 0:
        return _partial_match_response(partial_match_agencies)

    return _no_match_response()


def _partial_match_response(partial_match_agencies):
    return AgencyMatchResponse(
        status=AgencyMatchStatus.PARTIAL, agencies=partial_match_agencies
    )


def _exact_match_response(exact_match_agency):
    return AgencyMatchResponse(
        status=AgencyMatchStatus.EXACT, agencies=[exact_match_agency]
    )


def _no_match_response():
    return AgencyMatchResponse(
        status=AgencyMatchStatus.NO_MATCH,
    )


def _get_agencies(db_client, location_id):
    return db_client.get_agencies(
        columns=["id", "submitted_name"],
        where_mappings=WhereMapping.from_dict({"location_id": location_id}),
    )


def _get_location_id(db_client, dto):
    return db_client.get_location_id(
        where_mappings=WhereMapping.from_dict(
            {
                "state_name": dto.state,
                "county_name": dto.county,
                "locality_name": dto.locality,
            }
        )
    )
