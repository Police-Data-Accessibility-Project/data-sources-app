from utilities.common import convert_dates_to_strings

ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
]


def archives_get_results(conn):
    cursor = conn.cursor()
    sql_query = """
    SELECT
        airtable_uid,
        source_url,
        update_frequency,
        last_cached,
        broken_source_url_as_of
    FROM
        data_sources
    WHERE 
        (last_cached IS NULL OR update_frequency IS NOT NULL) AND broken_source_url_as_of IS NULL AND url_status <> 'broken' AND source_url IS NOT NULL
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
    sql_query = "UPDATE data_sources SET url_status = 'broken', broken_source_url_as_of = '{0}', last_cached = '{1}' WHERE airtable_uid = '{2}'"
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
