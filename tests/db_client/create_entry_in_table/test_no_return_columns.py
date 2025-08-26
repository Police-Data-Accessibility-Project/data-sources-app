from db.db_client_dataclasses import WhereMapping


def test_create_entry_in_table_no_return_columns(live_database_client, test_table_data):
    id = live_database_client._create_entry_in_table(
        table_name="test_table",
        column_value_mappings={
            "pet_name": "George",
            "species": "Monkey",
        },
    )

    assert id is None

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Monkey")],
    )

    assert results == [
        {"pet_name": "George"},
    ]
