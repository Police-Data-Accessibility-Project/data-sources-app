from db.client.core import DatabaseClient
from db.db_client_dataclasses import WhereMapping


def test_update_entry_in_table(live_database_client: DatabaseClient, test_table_data):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Cat")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]

    live_database_client._update_entry_in_table(
        table_name="test_table",
        entry_id="Jimbo",
        column_edit_mappings={"species": "Lion"},
        id_column_name="pet_name",
    )

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Cat")],
    )

    assert results == []

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Lion")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]
