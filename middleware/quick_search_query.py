import spacy
import json
import datetime
from utilities.common import convert_dates_to_strings, format_arrays

QUICK_SEARCH_SQL = """
    SELECT
        data_sources.airtable_uid,
        data_sources.name AS data_source_name,
        data_sources.description,
        data_sources.record_type,
        data_sources.source_url,
        data_sources.record_format,
        data_sources.coverage_start,
        data_sources.coverage_end,
        data_sources.agency_supplied,
        agencies.name AS agency_name,
        agencies.municipality,
        agencies.state_iso
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    INNER JOIN
        state_names ON agencies.state_iso = state_names.state_iso
    WHERE
        (data_sources.name ILIKE %s OR data_sources.description ILIKE %s OR data_sources.record_type ILIKE %s OR data_sources.tags ILIKE %s) 
        AND (agencies.county_name ILIKE %s OR concat(substr(agencies.county_name,3,length(agencies.county_name)-4), ' county') ILIKE %s 
            OR agencies.state_iso ILIKE %s OR agencies.municipality ILIKE %s OR agencies.agency_type ILIKE %s OR agencies.jurisdiction_type ILIKE %s 
            OR agencies.name ILIKE %s OR state_names.state_name ILIKE %s)
        AND data_sources.approval_status = 'approved'

"""


def quick_search_query(conn, search, location):
    data_sources = {"count": 0, "data": []}
    if type(conn) == dict:
        return data_sources

    search = "" if search == "all" else search
    location = "" if location == "all" else location

    # Depluralize search term to increase match potential
    nlp = spacy.load("en_core_web_sm")
    search = search.strip()
    doc = nlp(search)
    lemmatized_tokens = [token.lemma_ for token in doc]
    depluralized_search_term = " ".join(lemmatized_tokens)
    location = location.strip()

    cursor = conn.cursor()

    print(f"Query parameters: '%{depluralized_search_term}%', '%{location}%'")

    cursor.execute(
        QUICK_SEARCH_SQL,
        (
            f"%{depluralized_search_term}%",
            f"%{depluralized_search_term}%",
            f"%{depluralized_search_term}%",
            f"%{depluralized_search_term}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
            f"%{location}%",
        ),
    )
    results = cursor.fetchall()

    # If altered search term returns no results, try with unaltered search term
    if not results:
        print(f"Query parameters: '%{search}%', '%{location}%'")
        cursor.execute(
            QUICK_SEARCH_SQL,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
            ),
        )
        results = cursor.fetchall()

    column_names = [
        "airtable_uid",
        "data_source_name",
        "description",
        "record_type",
        "source_url",
        "record_format",
        "coverage_start",
        "coverage_end",
        "agency_supplied",
        "agency_name",
        "municipality",
        "state_iso",
    ]
    data_source_matches = [dict(zip(column_names, result)) for result in results]
    data_source_matches_converted = []
    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))

    data_sources = {
        "count": len(data_source_matches_converted),
        "data": data_source_matches_converted,
    }

    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    query_results = json.dumps(data_sources["data"])

    cursor_query_log = conn.cursor()
    sql_query_log = "INSERT INTO quick_search_query_logs (search, location, results, result_count, datetime_of_request) VALUES (%s, %s, %s, %s, %s)"
    cursor_query_log.execute(
        sql_query_log,
        (search, location, query_results, data_sources["count"], datetime_string),
    )
    conn.commit()

    return data_sources
