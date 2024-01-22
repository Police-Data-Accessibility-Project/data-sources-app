import spacy
import json
import datetime
from utilities.common import convert_dates_to_strings, format_arrays

QUICK_SEARCH_COLUMNS = [
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
        (data_sources.name LIKE '%{0}%' OR data_sources.description LIKE '%{0}%' OR data_sources.record_type LIKE '%{0}%' OR data_sources.tags LIKE '%{0}%') 
        AND (agencies.county_name LIKE '%{1}%' OR substr(agencies.county_name,3,length(agencies.county_name)-4) || ' county' LIKE '%{1}%' 
            OR agencies.state_iso LIKE '%{1}%' OR agencies.municipality LIKE '%{1}%' OR agencies.agency_type LIKE '%{1}%' OR agencies.jurisdiction_type LIKE '%{1}%' 
            OR agencies.name LIKE '%{1}%' OR state_names.state_name LIKE '%{1}%')
        AND data_sources.approval_status = 'approved'
        AND data_sources.url_status not in ('broken', 'none found')

"""

INSERT_LOG_QUERY = "INSERT INTO quick_search_query_logs (search, location, results, result_count, created_at, datetime_of_request) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{4}')"


def unaltered_search_query(cursor, search, location):
    print(f"Query parameters: '%{search}%', '%{location}%'")
    cursor.execute(QUICK_SEARCH_SQL.format(search.title(), location.title()))
    results = cursor.fetchall()

    return results


def spacy_search_query(cursor, search, location):
    # Depluralize search term to increase match potential
    nlp = spacy.load("en_core_web_sm")
    search = search.strip()
    doc = nlp(search)
    lemmatized_tokens = [token.lemma_ for token in doc]
    depluralized_search_term = " ".join(lemmatized_tokens)
    location = location.strip()

    print(f"Query parameters: '%{depluralized_search_term}%', '%{location}%'")

    cursor.execute(
        QUICK_SEARCH_SQL.format(depluralized_search_term.title(), location.title())
    )
    results = cursor.fetchall()

    return results


def quick_search_query(search="", location="", test_query_results=[], conn={}):
    data_sources = {"count": 0, "data": []}
    if type(conn) == dict and "data" in conn:
        return data_sources

    search = "" if search == "all" else search
    location = "" if location == "all" else location

    if conn:
        cursor = conn.cursor()

    unaltered_results = (
        unaltered_search_query(cursor, search, location)
        if not test_query_results
        else test_query_results
    )
    spacy_results = (
        spacy_search_query(cursor, search, location)
        if not test_query_results
        else test_query_results
    )

    # Compare altered search term results with unaltered search term results, return the longer list
    results = (
        spacy_results
        if len(spacy_results) > len(unaltered_results)
        else unaltered_results
    )

    data_source_matches = [
        dict(zip(QUICK_SEARCH_COLUMNS, result)) for result in results
    ]
    data_source_matches_converted = []
    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))

    data_sources = {
        "count": len(data_source_matches_converted),
        "data": data_source_matches_converted,
    }

    if not test_query_results:
        current_datetime = datetime.datetime.now()
        datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        query_results = json.dumps(data_sources["data"]).replace("'", "")

        cursor.execute(
            INSERT_LOG_QUERY.format(
                search, location, query_results, data_sources["count"], datetime_string
            ),
        )
        conn.commit()
        cursor.close()

    return data_sources
