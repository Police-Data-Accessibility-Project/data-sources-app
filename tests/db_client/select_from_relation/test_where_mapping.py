from db.client.core import DatabaseClient
from db.db_client_dataclasses import WhereMapping


def test_select_from_relation_where_mapping(
    live_database_client: DatabaseClient,
):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", eq=False, value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]
