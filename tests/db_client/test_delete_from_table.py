def test_delete_from_table(live_database_client, test_table_data):
    initial_results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
    )

    assert initial_results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]

    live_database_client._delete_from_table(
        table_name="test_table",
        id_column_name="species",
        id_column_value="Cat",
    )

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
    ]
