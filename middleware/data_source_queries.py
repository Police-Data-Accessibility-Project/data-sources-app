from utilities.common import convert_dates_to_strings, format_arrays

APPROVED_COLUMNS = [
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


def data_source_by_id_results(conn, data_source_id):
    cursor = conn.cursor()

    data_source_approved_columns = [
        f"data_sources.{approved_column}" for approved_column in APPROVED_COLUMNS
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
            {}
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

    return cursor.fetchone()


def data_source_by_id_query(data_source_id="", test_query_results=[], conn={}):
    if conn:
        result = data_source_by_id_results(conn, data_source_id)
    else:
        result = test_query_results

    if result:
        data_source_and_agency_columns = APPROVED_COLUMNS + AGENCY_APPROVED_COLUMNS
        data_source_and_agency_columns.append("data_source_id")
        data_source_and_agency_columns.append("agency_id")
        data_source_and_agency_columns.append("agency_name")
        data_source_details = dict(zip(data_source_and_agency_columns, result))
        data_source_details = convert_dates_to_strings(data_source_details)
        data_source_details = format_arrays(data_source_details)

    else:
        data_source_details = []

    return data_source_details


def data_sources_query(conn):
    data_source_approved_columns = [
        f"data_sources.{approved_column}" for approved_column in APPROVED_COLUMNS
    ]
    data_source_approved_columns.append("agencies.name as agency_name")

    joined_column_names = ", ".join(data_source_approved_columns)

    cursor = conn.cursor()
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

    data_source_output_columns = APPROVED_COLUMNS + ["agency_name"]

    data_source_matches = [
        dict(zip(data_source_output_columns, result)) for result in results
    ]
    data_source_matches_converted = []

    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))

    return data_source_matches_converted
