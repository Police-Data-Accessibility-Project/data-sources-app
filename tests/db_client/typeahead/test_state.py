def test_get_typeahead_locations_state(live_database_client):
    live_database_client.refresh_all_materialized_views()
    results = live_database_client.get_typeahead_locations(search_term="Pen")
    assert len(results) > 0

    assert results[0]["display_name"] == "Pennsylvania"
    assert results[0]["type"] == "State"
    assert results[0]["state_name"] == "Pennsylvania"
    assert results[0]["county_name"] is None
    assert results[0]["locality_name"] is None
