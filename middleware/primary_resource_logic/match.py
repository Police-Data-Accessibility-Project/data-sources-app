from enum import Enum
from typing import Optional, List

from flask import Response

from db.client import DatabaseClient
from db.db_client_dataclasses import WhereMapping
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.dtos.match_dtos import (
    AgencyMatchResponseOuterDTO,
    AgencyMatchRequestDTO,
    AgencyMatchResponseInnerDTO,
)


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

    def __init__(
        self,
        status: AgencyMatchStatus,
        agencies: Optional[list[AgencyMatchResponseInnerDTO]] = None,
    ):
        self.status = status
        self.agencies = agencies
        self.message = get_agency_match_message(status)

    def to_json(self):
        if self.agencies is None:
            agencies = []
        else:
            agencies = [agency.model_dump(mode="json") for agency in self.agencies]
        return {
            "status": self.status.value,
            "message": self.message,
            "agencies": agencies,
        }


def format_response(amr: AgencyMatchResponse) -> Response:
    return FlaskResponseManager.make_response(
        data=amr.to_json(),
    )


def match_agency_wrapper(db_client: DatabaseClient, dto: AgencyMatchResponseOuterDTO):
    result = try_matching_agency(db_client=db_client, dto=dto)
    return format_response(result)


def try_matching_agency(
    db_client: DatabaseClient, dto: AgencyMatchRequestDTO
) -> AgencyMatchResponse:

    location_id: Optional[int] = _get_location_id(db_client, dto)
    if location_id is None and dto.has_location_data():
        return _no_match_response()

    entries: list[AgencyMatchResponseInnerDTO] = db_client.get_similar_agencies(
        name=dto.name, location_id=location_id
    )
    if len(entries) == 0:
        return _no_match_response()

    if len(entries) == 1 and entries[0].similarity == 1:
        return _exact_match_response(entries[0])

    return _partial_match_response(entries)


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


def _get_location_id(db_client, dto: AgencyMatchRequestDTO):
    if dto.state is None and dto.county is None and dto.locality is None:
        return None
    return db_client.get_location_id(
        where_mappings=WhereMapping.from_dict(
            {
                "state_name": dto.state,
                "county_name": dto.county,
                "locality_name": dto.locality,
            }
        )
    )
