from db.client.core import DatabaseClient


def test_select_from_relation_columns_only(
    live_database_client: DatabaseClient, test_table_data
):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]
