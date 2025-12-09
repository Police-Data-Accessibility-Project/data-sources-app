def wipe_database(db_client):
    for table in [
        "agencies",
        "data_sources",
        "data_requests",
        "users",
        "meta_urls",
        "localities",
    ]:
        db_client.execute_raw_sql("DELETE FROM " + table)
