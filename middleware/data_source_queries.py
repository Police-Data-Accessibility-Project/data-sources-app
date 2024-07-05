from http import HTTPStatus
from typing import Any

from flask import make_response, Response


from database_client.database_client import DatabaseClient
from database_client.result_formatter import ResultFormatter
from utilities.common import convert_dates_to_strings, format_arrays


class DataSourceNotFoundError(Exception):
    pass


DATA_SOURCES_APPROVED_COLUMNS = [
    "name",
    "submitted_name",
    "description",
    "record_type",
    "source_url",
    "agency_supplied",
    "supplying_entity",
    "agency_originated",
    "originating_entity",
    "agency_aggregation",
    "coverage_start",
    "coverage_end",
    "source_last_updated",
    "retention_schedule",
    "detail_level",
    "number_of_records_available",
    "size",
    "access_type",
    "data_portal_type",
    "record_format",
    "update_frequency",
    "update_method",
    "tags",
    "readme_url",
    "scraper_url",
    "data_source_created",
    "airtable_source_last_modified",
    "url_status",
    "rejection_note",
    "last_approval_editor",
    "agency_described_submitted",
    "agency_described_not_in_database",
    "approval_status",
    "record_type_other",
    "data_portal_type_other",
    "records_not_online",
    "data_source_request",
    "url_button",
    "tags_other",
    "access_notes",
    "last_cached",
]

DATA_SOURCES_OUTPUT_COLUMNS = DATA_SOURCES_APPROVED_COLUMNS + ["agency_name"]

AGENCY_APPROVED_COLUMNS = [
    "homepage_url",
    "count_data_sources",
    "agency_type",
    "multi_agency",
    "submitted_name",
    "jurisdiction_type",
    "state_iso",
    "municipality",
    "zip_code",
    "county_fips",
    "county_name",
    "lat",
    "lng",
    "data_sources",
    "no_web_presence",
    "airtable_agency_last_modified",
    "data_sources_last_updated",
    "approved",
    "rejection_reason",
    "last_approval_editor",
    "agency_created",
    "county_airtable_uid",
    "defunct_year",
]


def get_approved_data_sources_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_approved_data_sources()
    zipped_results = ResultFormatter.zip_get_approved_data_sources_results(raw_results)
    return make_response(
        {
            "count": len(zipped_results),
            "data": zipped_results,
        },
        HTTPStatus.OK.value,
    )


def data_source_by_id_wrapper(arg, db_client: DatabaseClient) -> Response:
    try:
        data_source_details = data_source_by_id_query(
            data_source_id=arg, db_client=db_client
        )
        return make_response(data_source_details, HTTPStatus.OK.value)
    except DataSourceNotFoundError:
        return make_response({"message": "Data source not found."}, HTTPStatus.OK.value)


def get_data_sources_for_map_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_data_sources_for_map()
    zipped_results = ResultFormatter.zip_get_datas_sources_for_map_results(raw_results)
    return make_response(
        {
            "count": len(zipped_results),
            "data": zipped_results,
        },
        HTTPStatus.OK.value,
    )


def data_source_by_id_query(
    data_source_id: str,
    db_client: DatabaseClient,
) -> dict[str, Any]:
    """
    Processes a request to fetch data source details by ID from the database

    :param data_source_id: The unique identifier for the data source.
    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :return: A dictionary with the data source details after processing.
    """
    raw_results = db_client.get_data_source_by_id(data_source_id)
    if not raw_results:
        raise DataSourceNotFoundError("The specified data source was not found.")

    return ResultFormatter.zip_get_data_source_by_id_results(raw_results)


def get_restricted_columns():
    restricted_columns = [
        "rejection_note",
        "data_source_request",
        "approval_status",
        "airtable_uid",
        "airtable_source_last_modified",
    ]
    return restricted_columns

def update_data_source_wrapper(
    db_client: DatabaseClient, data: dict, data_source_id: str
) -> Response:
    db_client.update_data_source(data, data_source_id)
    return make_response(
        {"message": "Data source updated successfully."}, HTTPStatus.OK
    )


def add_new_data_source_wrapper(db_client: DatabaseClient, data: dict) -> Response:
    db_client.add_new_data_source(data)
    return make_response({"message": "Data source added successfully."}, HTTPStatus.OK)


def needs_identification_data_sources_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_needs_identification_data_sources()
    zipped_results = ResultFormatter.zip_needs_identification_data_source_results(
        raw_results
    )
    return make_response(
        {
            "count": len(zipped_results),
            "data": zipped_results,
        },
        HTTPStatus.OK.value,
    )


def convert_data_source_matches(
    data_source_output_columns: list[str], results: list[tuple]
) -> dict:
    """
    Combine a list of output columns with a list of results,
    and produce a list of dictionaries where the keys correspond
    to the output columns and the values correspond to the results
    :param data_source_output_columns:
    :param results:
    :return:
    """
    data_source_matches = [
        dict(zip(data_source_output_columns, result)) for result in results
    ]
    data_source_matches_converted = []
    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))
    return data_source_matches_converted
