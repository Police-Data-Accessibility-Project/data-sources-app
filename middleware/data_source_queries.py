from typing import Any, Dict, List, Optional
import sqlite3
from utilities.common import convert_dates_to_strings, format_arrays

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


def data_source_by_id_results(conn: sqlite3.Connection, data_source_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves detailed information for a specific data source by its ID, combining fields from both the data_sources and agencies tables.

    Parameters:
    - conn: sqlite3.Connection object to execute the query on the database.
    - data_source_id: The unique identifier for the data source.

    Returns:
    - A dictionary containing the combined details of the data source and its associated agency, if found; otherwise, None.
    """
    cursor = conn.cursor()

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
            data_sources.approval_status = 'approved' AND data_sources.airtable_uid = '{1}'
    """.format(
        joined_column_names, data_source_id
    )

    cursor.execute(sql_query)
    result = cursor.fetchone()
    cursor.close()

    return result

def data_source_by_id_query(data_source_id: str = "", test_query_results: Optional[List[Dict[str, Any]]] = None,
                            conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """
    Processes a query to fetch details for a specific data source by its ID, optionally using test data for the results.

    Parameters:
    - data_source_id: The unique identifier for the data source. Used if test_query_results is not provided.
    - test_query_results: Optional; predefined results for testing purposes.
    - conn: Optional; sqlite3.Connection object for database access if test_query_results is not provided.

    Returns:
    - A dictionary with the details of the data source and its associated agency.
    """
    if conn:
        result = data_source_by_id_results(conn, data_source_id)
    else:
        result = test_query_results

    if result:
        data_source_and_agency_columns = (
            DATA_SOURCES_APPROVED_COLUMNS + AGENCY_APPROVED_COLUMNS
        )
        data_source_and_agency_columns.append("data_source_id")
        data_source_and_agency_columns.append("agency_id")
        data_source_and_agency_columns.append("agency_name")
        data_source_details = dict(zip(data_source_and_agency_columns, result))
        data_source_details = convert_dates_to_strings(data_source_details)
        data_source_details = format_arrays(data_source_details)

    else:
        data_source_details = []

    return data_source_details


def data_sources_results(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Fetches approved data sources from the database, including related agency information.

    Parameters:
    - conn: sqlite3.Connection object to execute the query on the database.

    Returns:
    - A list of dictionaries, each representing an approved data source with its associated agency name.
    """
    cursor = conn.cursor()
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
    cursor.close()

    return results


def data_sources_query(conn: Optional[sqlite3.Connection] = None,
                       test_query_results: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Queries and processes a list of approved data sources, optionally using test data.

    Parameters:
    - conn: Optional; sqlite3.Connection object for database access if test_query_results is not provided.
    - test_query_results: Optional; predefined results for testing purposes.

    Returns:
    - A list of dictionaries, each containing details of an approved data source and its associated agency name.
    """
    results = data_sources_results(conn, "", "") if conn else test_query_results

    data_source_output_columns = DATA_SOURCES_APPROVED_COLUMNS + ["agency_name"]

    data_source_matches = [
        dict(zip(data_source_output_columns, result)) for result in results
    ]
    data_source_matches_converted = []

    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))

    return data_source_matches_converted
