from typing import List, Dict, Any, Optional, Tuple, Union
from utilities.common import convert_dates_to_strings, format_arrays
from psycopg2.extensions import connection as PgConnection

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


def data_source_by_id_results(
    conn: PgConnection, data_source_id: str
) -> Union[tuple[Any, ...], None]:
    """
    Fetches a single data source by its ID, including related agency information, from a PostgreSQL database.

    :param conn: A psycopg2 connection object to a PostgreSQL database.
    :param data_source_id: The unique identifier for the data source.
    :return: A dictionary containing the data source and its related agency details.
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


def data_source_by_id_query(
    data_source_id: str = "",
    test_query_results: Optional[List[Dict[str, Any]]] = None,
    conn: Optional[PgConnection] = None,
) -> Dict[str, Any]:
    """
    Processes a request to fetch data source details by ID, either from the database or provided test results.

    :param data_source_id: The unique identifier for the data source.
    :param test_query_results: A list of dictionaries representing test query results, if provided.
    :param conn: A psycopg2 connection object to a PostgreSQL database.
    :return: A dictionary with the data source details after processing.
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


def get_approved_data_sources(conn: PgConnection) -> list[tuple[Any, ...]]:
    """
    Fetches all approved data sources and their related agency information from a PostgreSQL database.

    :param conn: A psycopg2 connection object to a PostgreSQL database.
    :return: A list of dictionaries, each containing details of a data source and its related agency.
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


def needs_identification_data_sources(conn) -> list:
    """
    Returns a list of data sources that need identification
    """
    cursor = conn.cursor()
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
    cursor.close()

    return results


def get_data_sources_for_map(conn) -> list:
    """
    Returns a list of data sources with relevant info for the map
    """
    cursor = conn.cursor()
    sql_query = """
        SELECT
            data_sources.airtable_uid as data_source_id,
            data_sources.name,
            agencies.airtable_uid as agency_id,
            agencies.submitted_name as agency_name,
            agencies.state_iso,
            agencies.municipality,
            agencies.county_name,
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
    cursor.close()

    return results


def data_sources_query(
    conn: Optional[PgConnection] = None,
    test_query_results: Optional[List[Dict[str, Any]]] = None,
    approval_status: str = "approved",
    for_map: bool = False,
) -> List[Dict[str, Any]]:
    """
    Processes and formats a list of approved data sources, with an option to use test query results.

    :param approval_status: The approval status of the data sources to query.
    :param conn: Optional psycopg2 connection object to a PostgreSQL database.
    :param test_query_results: Optional list of test query results to use instead of querying the database.
    :return: A list of dictionaries, each formatted with details of a data source and its associated agency.
    """
    if for_map:
        results = get_data_sources_for_map(conn)
    elif conn and approval_status == "approved":
        results = get_approved_data_sources(conn)
    elif conn and not for_map:
        results = needs_identification_data_sources(conn)
    else:
        results = test_query_results

    if not for_map:
        data_source_output_columns = DATA_SOURCES_APPROVED_COLUMNS + ["agency_name"]
    else:
        data_source_output_columns = [
            "data_source_id",
            "name",
            "agency_id",
            "agency_name",
            "state_iso",
            "municipality",
            "county_name",
            "lat",
            "lng",
        ]

    data_source_matches = [
        dict(zip(data_source_output_columns, result)) for result in results
    ]
    data_source_matches_converted = []

    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))

    return data_source_matches_converted
