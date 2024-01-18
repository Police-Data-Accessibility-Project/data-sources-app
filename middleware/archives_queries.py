from utilities.common import convert_dates_to_strings

ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
    "agency_name",
]


def archives_get_results(conn):
    cursor = conn.cursor()
    sql_query = """
    SELECT
    data_sources.airtable_uid,
    data_sources.source_url,
    data_sources.update_frequency,
    data_sources.last_cached,
    data_sources.broken_source_url_as_of,
    agencies.name
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    WHERE 
        (data_sources.last_cached IS NULL OR data_sources.update_frequency IS NOT NULL) AND data_sources.broken_source_url_as_of IS NULL AND data_sources.source_url IS NOT NULL
    """
    cursor.execute(sql_query)

    return cursor.fetchall()


def archives_get_query(test_query_results=[], conn={}):
    results = (
        archives_get_results(conn) if not test_query_results else test_query_results
    )
    archives_combined_results = [
        dict(zip(ARCHIVES_GET_COLUMNS, result)) for result in results
    ]
    archives_combined_results_clean = []
    for item in archives_combined_results:
        archives_combined_results_clean.append(convert_dates_to_strings(item))

    return archives_combined_results_clean


def archives_put_broken_as_of_results(id, broken_as_of, last_cached, conn):
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET broken_source_url_as_of = '{0}', last_cached = '{1}' WHERE airtable_uid = '{2}'"
    cursor.execute(sql_query.format(broken_as_of, last_cached, id))
    cursor.close()


def archives_put_last_cached_results(id, last_cached, conn):
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET last_cached = '{0}' WHERE airtable_uid = '{1}'"
    cursor.execute(sql_query.format(last_cached, id))
    cursor.close()


def archives_put_query(id="", broken_as_of="", last_cached="", conn={}):
    if broken_as_of:
        archives_put_broken_as_of_results(id, broken_as_of, last_cached, conn)
    else:
        archives_put_last_cached_results(id, last_cached, conn)

    conn.commit()
