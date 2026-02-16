def wipe_database(db_client):
    for table in [
        "change_log",
        "table_count_log",
        "notification_log",
        "agencies",
        "data_sources",
        "data_requests",
        "users",
        "meta_urls",
        "localities",
    ]:
        db_client.execute_raw_sql("DELETE FROM " + table)
