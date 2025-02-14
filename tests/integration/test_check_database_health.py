from unittest.mock import MagicMock, call

from middleware.scheduled_tasks.check_database_health import check_database_health_inner

def wipe_database(db_client):
    for table in ["agencies", "data_sources", "data_requests", "users"]:
        db_client.execute_raw_sql("DELETE FROM " + table)


def test_check_database_health(test_data_creator_db_client, monkeypatch):
    tdc = test_data_creator_db_client
    db_client = tdc.db_client

    wipe_database(db_client)

    mock_send_alert = MagicMock()
    monkeypatch.setattr(
        "middleware.scheduled_tasks.check_database_health.send_alert", mock_send_alert
    )
    check_database_health_inner(db_client)

    # Get results from database
    tcrm = db_client.get_most_recent_logged_table_counts()

    tcrs = tcrm.get_table_references()
    for tcr in tcrs:
        assert tcr.count == 0

    # Add 20 agencies (which will trigger an alert)
    for i in range(20):
        tdc.agency()

    check_database_health_inner(db_client)
    mock_send_alert.assert_has_calls(
        calls=[
            call("Sudden change in agencies table: 0 -> 20"),
        ]
    )

    tcrm = db_client.get_most_recent_logged_table_counts()
    tcrs = tcrm.get_table_references()

    assert tcrm.get_table_count("agencies") == 20

    # Add 1 agency (which should not trigger an alert)
    tdc.agency()

    check_database_health_inner(db_client)
    mock_send_alert.assert_has_calls(
        calls=[
            call("Sudden change in agencies table: 0 -> 20"),
        ]
    )

    tcrm = db_client.get_most_recent_logged_table_counts()
    tcrs = tcrm.get_table_references()

    assert tcrm.get_table_count("agencies") == 21
