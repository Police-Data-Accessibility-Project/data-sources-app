from db.client.core import DatabaseClient


def test_select_from_relation_limit(live_database_client: DatabaseClient):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        limit=1,
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]
