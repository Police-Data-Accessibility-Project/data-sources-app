import uuid
from datetime import datetime
from http import HTTPStatus
from typing import List, Dict, Any, Optional, Tuple, Union

from flask import make_response, Response
from sqlalchemy.dialects.postgresql import psycopg2

from utilities.common import convert_dates_to_strings, format_arrays
from psycopg2.extensions import connection as PgConnection
import psycopg2

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

DATA_SOURCES_MAP_COLUMN = [
    "data_source_id",
    "name",
    "agency_id",
    "agency_name",
    "state_iso",
    "municipality",
    "county_name",
    "record_type",
    "lat",
    "lng",
]


def get_approved_data_sources_wrapper(cursor: psycopg2.extensions.cursor) -> Response:
    data_source_matches = get_approved_data_sources(cursor)

    return make_response(
        {
            "count": len(data_source_matches),
            "data": data_source_matches,
        },
        HTTPStatus.OK.value,
    )


def data_source_by_id_wrapper(arg, cursor: psycopg2.extensions.cursor) -> Response:
    data_source_details = data_source_by_id_query(data_source_id=arg, cursor=cursor)
    if data_source_details:
        return make_response(data_source_details, HTTPStatus.OK.value)

    else:
        return make_response({"message": "Data source not found."}, HTTPStatus.OK.value)


def get_data_sources_for_map_wrapper(cursor: psycopg2.extensions.cursor) -> Response:
    data_source_details = get_data_sources_for_map(cursor)
    return make_response(
        {
            "count": len(data_source_details),
            "data": data_source_details,
        },
        HTTPStatus.OK.value,
    )


def data_source_by_id_results(
    cursor: psycopg2.extensions.cursor, data_source_id: str
) -> Union[tuple[Any, ...], None]:
    """
    Fetches a single data source by its ID, including related agency information, from a PostgreSQL database.

    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :param data_source_id: The unique identifier for the data source.
    :return: A dictionary containing the data source and its related agency details.
    """

    data_source_approved_columns = [
        f"data_sources.{approved_column}"
        for approved_column in DATA_SOURCES_APPROVED_COLUMNS
    ]
    agencies_approved_columns = [
        f"agencies.{field}" for field in AGENCY_APPROVED_COLUMNS
    ]
    all_approved_columns = data_source_approved_columns + agencies_approved_columns
    all_approved_columns.append("data_sources.airtable_uid as data_source_id")
    all_approved_columns.append("agencies.airtable_uid as agency_id")
    all_approved_columns.append("agencies.name as agency_name")

    joined_column_names = ", ".join(all_approved_columns)
    sql_query = """
        SELECT
            {0}
        FROM
            agency_source_link
        INNER JOIN
            data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
        INNER JOIN
            agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
        WHERE
            data_sources.approval_status = 'approved' AND data_sources.airtable_uid = %s
    """.format(
        joined_column_names
    )

    cursor.execute(sql_query, (data_source_id,))
    result = cursor.fetchone()

    return result


def data_source_by_id_query(
    data_source_id: str,
    cursor: psycopg2.extensions.cursor,
) -> Dict[str, Any]:
    """
    Processes a request to fetch data source details by ID from the database

    :param data_source_id: The unique identifier for the data source.
    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :return: A dictionary with the data source details after processing.
    """
    result = data_source_by_id_results(cursor, data_source_id)
    if not result:
        return []

    data_source_and_agency_columns = (
        DATA_SOURCES_APPROVED_COLUMNS + AGENCY_APPROVED_COLUMNS
    )
    data_source_and_agency_columns.append("data_source_id")
    data_source_and_agency_columns.append("agency_id")
    data_source_and_agency_columns.append("agency_name")
    data_source_details = dict(zip(data_source_and_agency_columns, result))
    data_source_details = convert_dates_to_strings(data_source_details)
    data_source_details = format_arrays(data_source_details)

    return data_source_details


def update_data_source(
    cursor: psycopg2.extensions.cursor, data: dict, data_source_id: str
) -> Response:
    """
    Processes a request to update the data source

    :param data_source_id:
    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :param data: A dictionary containing the data source details.
    :return: A dictionary containing a message about the update operation
    """
    sql_query = create_data_source_update_query(data, data_source_id)
    cursor.execute(sql_query)
    return make_response(
        {"message": "Data source updated successfully."}, HTTPStatus.OK
    )


def create_data_source_update_query(data: dict, data_source_id: str) -> str:
    restricted_columns = get_restricted_columns()
    data_to_update = ""
    for key, value in data.items():
        if key not in restricted_columns:
            if type(value) == str:
                data_to_update += f"{key} = '{value}', "
            else:
                data_to_update += f"{key} = {value}, "
    data_to_update = data_to_update[:-2]
    sql_query = f"""
    UPDATE data_sources 
    SET {data_to_update}
    WHERE airtable_uid = '{data_source_id}'
    """
    return sql_query


def create_new_data_source_query(data: dict) -> str:
    restricted_columns = get_restricted_columns()
    column_names = ""
    column_values = ""
    for key, value in data.items():
        if key not in restricted_columns:
            column_names += f"{key}, "
            if type(value) == str:
                column_values += f"'{value}', "
            else:
                column_values += f"{value}, "

    now = datetime.now().strftime("%Y-%m-%d")
    airtable_uid = str(uuid.uuid4())

    column_names += "approval_status, url_status, data_source_created, airtable_uid"
    column_values += f"False, '[\"ok\"]', '{now}', '{airtable_uid}'"

    sql_query = f"INSERT INTO data_sources ({column_names}) VALUES ({column_values}) RETURNING *"

    return sql_query


def add_new_data_source(cursor: psycopg2.extensions.cursor, data: dict) -> Response:
    """
    Processes a request to add a new data source

    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :param data: A dictionary containing the data source details.
    :return: A dictionary containing a message about the addition operation
    """
    sql_query = create_new_data_source_query(data)
    cursor.execute(sql_query)
    return make_response({"message": "Data source added successfully."}, HTTPStatus.OK)


def get_restricted_columns():
    restricted_columns = [
        "rejection_note",
        "data_source_request",
        "approval_status",
        "airtable_uid",
        "airtable_source_last_modified",
    ]
    return restricted_columns


def get_approved_data_sources(cursor: psycopg2.extensions.cursor) -> list[tuple[Any, ...]]:
    """
    Fetches all approved data sources and their related agency information from a PostgreSQL database.

    :param cursor: A psycopg2 connection object to a PostgreSQL database.
    :return: A list of dictionaries, each containing details of a data source and its related agency.
    """
    data_source_approved_columns = [
        f"data_sources.{approved_column}"
        for approved_column in DATA_SOURCES_APPROVED_COLUMNS
    ]
    data_source_approved_columns.append("agencies.name as agency_name")

    joined_column_names = ", ".join(data_source_approved_columns)

    sql_query = """
        SELECT
            {}
        FROM
            agency_source_link
        INNER JOIN
            data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
        INNER JOIN
            agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
        WHERE
            data_sources.approval_status = 'approved'
    """.format(
        joined_column_names
    )
    cursor.execute(sql_query)
    results = cursor.fetchall()

    return convert_data_source_matches(DATA_SOURCES_OUTPUT_COLUMNS, results)


def needs_identification_data_sources(cursor: psycopg2.extensions.cursor) -> dict:
    """
    Returns a list of data sources that need identification
    """
    joined_column_names = ", ".join(DATA_SOURCES_APPROVED_COLUMNS)

    sql_query = """
        SELECT
            {}
        FROM
            data_sources
        WHERE
            approval_status = 'needs identification'
    """.format(
        joined_column_names
    )
    cursor.execute(sql_query)
    results = cursor.fetchall()

    return convert_data_source_matches(DATA_SOURCES_OUTPUT_COLUMNS, results)


def get_data_sources_for_map(cursor: psycopg2.extensions.cursor) -> list:
    """
    Returns a list of data sources with relevant info for the map
    """
    sql_query = """
        SELECT
            data_sources.airtable_uid as data_source_id,
            data_sources.name,
            agencies.airtable_uid as agency_id,
            agencies.submitted_name as agency_name,
            agencies.state_iso,
            agencies.municipality,
            agencies.county_name,
            data_sources.record_type,
            agencies.lat,
            agencies.lng
        FROM
            agency_source_link
        INNER JOIN
            data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
        INNER JOIN
            agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
        WHERE
            data_sources.approval_status = 'approved'
    """
    cursor.execute(sql_query)
    results = cursor.fetchall()

    return convert_data_source_matches(DATA_SOURCES_MAP_COLUMN, results)


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
