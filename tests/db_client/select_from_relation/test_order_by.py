from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from db.enums import SortOrder


def test_select_from_relation_order_by(live_database_client: DatabaseClient):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        order_by=OrderByParameters(sort_by="species", sort_order=SortOrder.ASCENDING),
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
        {"pet_name": "Jimbo"},
    ]
