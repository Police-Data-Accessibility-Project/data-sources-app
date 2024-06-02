import psycopg2
from flask import Response, make_response

SQL_GET_AGENCIES_WITHOUT_HOMEPAGE_URLS = """
    SELECT
        SUBMITTED_NAME,
        JURISDICTION_TYPE,
        STATE_ISO,
        MUNICIPALITY,
        COUNTY_NAME,
        AIRTABLE_UID,
        COUNT_DATA_SOURCES,
        ZIP_CODE,
        NO_WEB_PRESENCE -- Relevant
    FROM
        PUBLIC.AGENCIES
    WHERE 
        approved = true
        AND homepage_url is null
        AND NOT EXISTS (
            SELECT 1 FROM PUBLIC.AGENCY_URL_SEARCH_CACHE
            WHERE PUBLIC.AGENCIES.AIRTABLE_UID = PUBLIC.AGENCY_URL_SEARCH_CACHE.agency_airtable_uid
        )
    ORDER BY COUNT_DATA_SOURCES DESC
    LIMIT 100 -- Limiting to 100 in acknowledgment of the search engine quota
"""

SQL_UPDATE_CACHE = """
    INSERT INTO public.agency_url_search_cache
    (agency_airtable_uid, search_result)
    VALUES (%s, %s)
"""


def get_agencies_without_homepage_urls(cursor: psycopg2.extensions.cursor) -> Response:
    cursor.execute(SQL_GET_AGENCIES_WITHOUT_HOMEPAGE_URLS)
    results = cursor.fetchall()
    output = []
    for result in results:
        dict_result = dict(zip([i[0] for i in cursor.description], result))
        output.append(dict_result)
    return make_response(output, 200)


def update_search_cache(
    cursor: psycopg2.extensions.cursor, agency_uid: str, search_results: list[str]
) -> Response:
    for result in search_results:
        cursor.execute(SQL_UPDATE_CACHE, (agency_uid, result))
    return make_response("Search Cache Updated", 200)
