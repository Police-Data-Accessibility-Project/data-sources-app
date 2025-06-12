from db.client import DatabaseClient
from middleware.miscellaneous.table_count_logic import TableCountReferenceManager
from middleware.third_party_interaction_logic.discord import DiscordPoster

TABLES_TO_CHECK = [
    "agencies",
    "data_sources",
    "data_requests",
    "users",
]

THRESHOLD = 1.05  # 5%


def check_database_health():
    """
    Checks database integrity by ensuring tables are not unexpectedly empty
    and that table sizes have not drastically changed.
    """

    print("Checking database health...")
    db_client = DatabaseClient()
    check_database_health_inner(db_client)


def check_database_health_inner(db_client):
    tcrm = check_table_counts_and_alert_if_exceeded(db_client)
    updated_table_counts = tcrm.get_modified_table_references()
    db_client.log_table_counts(updated_table_counts)


def check_table_counts_and_alert_if_exceeded(db_client):
    tcrm: TableCountReferenceManager = db_client.get_most_recent_logged_table_counts()
    for table in TABLES_TO_CHECK:
        prev_count = tcrm.get_table_count(table)
        new_count = db_client.get_table_count(table)
        is_new = prev_count is None
        tcrm.add_table_count(table, new_count, is_new)

        if is_new:
            continue
        # If ratio of new count to previous count is greater than the threshold, report an error
        if change_exceeds_ratio(new_count, prev_count):
            send_alert(f"Sudden change in {table} table: {prev_count} -> {new_count}")
    return tcrm


def change_exceeds_ratio(new_count, prev_count):
    abs_diff = abs(new_count - prev_count) + 1  # Prevent dividing by 0
    prev_count = prev_count + 1
    return abs_diff / prev_count > THRESHOLD


def send_alert(message):
    """
    Send alert to discord
    """
    DiscordPoster().post_to_discord(message)
