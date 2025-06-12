from csv import DictWriter
from http import HTTPStatus
from io import BytesIO, StringIO
from typing import Optional

from flask import Response, make_response, send_file
from pydantic import BaseModel

from db.client import DatabaseClient
from db.db_client_dataclasses import WhereMapping
from middleware.access_logic import AccessInfoPrimary
from middleware.dynamic_request_logic.post import PostLogic
from middleware.enums import JurisdictionSimplified, Relations, OutputFormatEnum
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO
from middleware.common_response_formatting import message_response
from middleware.util.datetime import get_datetime_now
from utilities.enums import RecordCategories


def get_jurisdiction_type_enum(
    jurisdiction_type_str: str,
) -> Optional[JurisdictionSimplified]:
    if jurisdiction_type_str in [
        "local",
        "school",
        "military",
        "tribal",
        "transit",
        "port",
    ]:
        return JurisdictionSimplified.LOCALITY
    return JurisdictionSimplified(jurisdiction_type_str)


def format_search_results(search_results: list[dict]) -> dict:
    """
    Convert results to the following format:

    {
      "count": <number>,
      "data": {
          "federal": {
            "count": <number>,
            "results": [<data-source-record>]
          }
          "state": {
            "count": <number>,
            "results": [<data-source-record>]
          },
          county: {
            "count": <number>,
            "results": [<data-source-record>]
          },
          locality: {
            "count": <number>,
            "results": [<data-source-record>]
          },
        }
    }

    :param search_results:
    :return:
    """

    response = {"count": 0, "data": {}}

    data = response["data"]
    # Create sub-dictionary for each jurisdiction
    for jurisdiction in [j.value for j in JurisdictionSimplified]:
        data[jurisdiction] = {"count": 0, "results": []}

    for result in search_results:
        jurisdiction_str = result.get("jurisdiction_type")
        jurisdiction = get_jurisdiction_type_enum(jurisdiction_str)
        data[jurisdiction.value]["count"] += 1
        data[jurisdiction.value]["results"].append(result)
        response["count"] += 1

    return response


def format_as_csv(ld: list[dict]) -> BytesIO:
    string_output = StringIO()
    writer = DictWriter(string_output, fieldnames=list(ld[0].keys()))
    writer.writeheader()
    writer.writerows(ld)
    string_output.seek(0)
    bytes_output = string_output.getvalue().encode("utf-8")
    return BytesIO(bytes_output)


def create_search_record(access_info, db_client, dto):
    db_client.create_search_record(
        user_id=access_info.get_user_id(),
        location_id=dto.location_id,
        # Pass originally provided record categories
        record_categories=dto.record_categories,
        record_types=dto.record_types,
    )


def send_search_results(search_results: list[dict], output_format: OutputFormatEnum):
    if output_format == OutputFormatEnum.JSON:
        return send_as_json(search_results)
    elif output_format == OutputFormatEnum.CSV:
        return send_as_csv(search_results)
    else:
        FlaskResponseManager.abort(
            message="Invalid output format.",
            code=HTTPStatus.BAD_REQUEST,
        )


def send_as_json(search_results):
    formatted_search_results = format_search_results(search_results)
    return make_response(formatted_search_results, HTTPStatus.OK)


def send_as_csv(search_results):
    filename = f"search_results-{get_datetime_now()}.csv"
    csv_stream = format_as_csv(ld=search_results)
    return send_file(
        csv_stream, download_name=filename, mimetype="text/csv", as_attachment=True
    )


def get_explicit_record_categories(
    record_categories=Optional[list[RecordCategories]],
) -> Optional[list[RecordCategories]]:
    if record_categories is None:
        return None
    if RecordCategories.ALL in record_categories:
        if len(record_categories) > 1:
            FlaskResponseManager.abort(
                message="ALL cannot be provided with other record categories.",
                code=HTTPStatus.BAD_REQUEST,
            )
        return [rc for rc in RecordCategories if rc != RecordCategories.ALL]
    return record_categories


def try_getting_location_id_and_raise_error_if_not_found(
    db_client: DatabaseClient,
    dto: SearchRequestsDTO,
) -> int:
    where_mappings = WhereMapping.from_dict(
        {
            "state_name": dto.state,
            "county_name": dto.county,
            "locality_name": dto.locality,
        }
    )

    location_id = db_client.get_location_id(
        where_mappings=where_mappings,
    )
    if not location_id:
        FlaskResponseManager.abort(
            message="Location not found.",
            code=HTTPStatus.BAD_REQUEST,
        )
    return location_id


def get_user_followed_search_link(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    location_id: int,
) -> Optional[int]:
    result = db_client._select_single_entry_from_relation(
        relation_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
        where_mappings={
            "user_id": access_info.get_user_id(),
            "location_id": location_id,
        },
        columns=["id"],
    )
    if result is None:
        return None
    return result["id"]


class FollowedSearchPostLogic(PostLogic):
    def make_response(self) -> Response:
        return message_response(
            message=f"Location followed.",
        )


def get_link_id_and_raise_error_if_not_found(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: SearchRequestsDTO
):
    location_id = try_getting_location_id_and_raise_error_if_not_found(
        db_client=db_client,
        dto=dto,
    )
    return get_user_followed_search_link(
        db_client=db_client,
        access_info=access_info,
        location_id=location_id,
    )


def get_location_link_and_raise_error_if_not_found(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestsDTO,
):
    link_id = get_user_followed_search_link(
        db_client=db_client,
        access_info=access_info,
        location_id=dto.location_id,
    )
    return LocationLink(link_id=link_id, location_id=dto.location_id)


class LocationLink(BaseModel):
    link_id: Optional[int]
    location_id: int
