from http import HTTPStatus
from typing import Optional

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.access_logic import AccessInfo
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.post_logic import post_entry, PostLogic
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters, IDInfo
from middleware.enums import JurisdictionSimplified, Relations
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import SearchRequests
from middleware.common_response_formatting import message_response
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

    # Create sub-dictionary for each jurisdiction
    for jurisdiction in [j.value for j in JurisdictionSimplified]:
        response["data"][jurisdiction] = {"count": 0, "results": []}

    for result in search_results:
        jurisdiction_str = result.get("jurisdiction_type")
        jurisdiction = get_jurisdiction_type_enum(jurisdiction_str)
        response["data"][jurisdiction.value]["count"] += 1
        response["data"][jurisdiction.value]["results"].append(result)
        response["count"] += 1

    return response


def search_wrapper(
        db_client: DatabaseClient,
        access_info: AccessInfo,
        dto: SearchRequests,
) -> Response:
    location_id = try_getting_location_id_and_raise_error_if_not_found(
        db_client=db_client,
        dto=dto,
    )
    explicit_record_categories = get_explicit_record_categories(dto.record_categories)
    db_client.create_search_record(
        user_id=access_info.get_user_id(),
        location_id=location_id,
        # Pass originally provided record categories
        record_categories=dto.record_categories,
    )
    search_results = db_client.search_with_location_and_record_type(
        state=dto.state,
        # Pass modified record categories, which breaks down ALL into individual categories
        record_categories=explicit_record_categories,
        county=dto.county,
        locality=dto.locality,
    )
    formatted_search_results = format_search_results(search_results)
    return make_response(formatted_search_results, HTTPStatus.OK)


def get_explicit_record_categories(record_categories = list[RecordCategories]) -> list[RecordCategories]:
    if record_categories == [RecordCategories.ALL]:
        return [rc for rc in RecordCategories if rc != RecordCategories.ALL]
    elif len(record_categories) > 1 and RecordCategories.ALL in record_categories:
        FlaskResponseManager.abort(
            message="ALL cannot be provided with other record categories.",
            code=HTTPStatus.BAD_REQUEST,
        )
    return record_categories


def try_getting_location_id_and_raise_error_if_not_found(
        db_client: DatabaseClient,
        dto: SearchRequests,
) -> int:
    where_mappings = WhereMapping.from_dict({
        "state_name": dto.state,
        "county_name": dto.county,
        "locality_name": dto.locality,
    })

    location_id = db_client.get_location_id(
        where_mappings=where_mappings,
    )
    if not location_id:
        FlaskResponseManager.abort(
            message="Location not found.",
            code=HTTPStatus.BAD_REQUEST,
        )
    return location_id


def get_followed_searches(
        db_client: DatabaseClient,
        access_info: AccessInfo,
) -> Response:
    results = db_client.get_user_followed_searches(
        left_id=access_info.get_user_id(),
    )
    results["message"] = "Followed searches found."
    return FlaskResponseManager.make_response(results)


def get_user_followed_search_link(
        db_client: DatabaseClient,
        access_info: AccessInfo,
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

def create_followed_search(
        db_client: DatabaseClient,
        access_info: AccessInfo,
        dto: SearchRequests,
) -> Response:
    # Get location id. If not found, not a valid location. Raise error
    location_id = try_getting_location_id_and_raise_error_if_not_found(
        db_client=db_client,
        dto=dto,
    )
    link_id = get_user_followed_search_link(
        db_client=db_client,
        access_info=access_info,
        location_id=location_id,
    )
    if link_id is not None:
        return message_response(
            message="Location already followed.",
        )

    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            entry_name="followed search",
            relation=Relations.LINK_USER_FOLLOWED_LOCATION.value,
            db_client_method=DatabaseClient.create_followed_search,
            access_info=access_info
        ),
        entry={
            "user_id": access_info.get_user_id(),
            "location_id": location_id,
        },
        check_for_permission=False,
        post_logic_class=FollowedSearchPostLogic
    )


def delete_followed_search(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    dto: SearchRequests,
) -> Response:
    # Get location id. If not found, not a valid location. Raise error
    location_id = try_getting_location_id_and_raise_error_if_not_found(
        db_client=db_client,
        dto=dto,
    )
    link_id = get_user_followed_search_link(
        db_client=db_client,
        access_info=access_info,
        location_id=location_id,
    )
    # Check if search is followed. If not, end early .
    if link_id is None:
        return message_response(
            message="Location not followed.",
        )

    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            entry_name="Followed search",
            relation=Relations.LINK_USER_FOLLOWED_LOCATION.value,
            db_client_method=DatabaseClient.delete_followed_search,
            access_info=access_info
        ),
        id_info=IDInfo(
            id_column_name="id",
            id_column_value=link_id,
        ),
    )
