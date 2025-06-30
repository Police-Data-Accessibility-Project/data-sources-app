def test_get_typeahead_locations_locality(live_database_client, pittsburgh_id):
    live_database_client.refresh_all_materialized_views()
    results = live_database_client.get_typeahead_locations(search_term="Pit")
    assert len(results) > 0

    assert results[0]["display_name"] == "Pittsburgh, Allegheny, Pennsylvania"
    assert results[0]["type"] == "Locality"
    assert results[0]["state_name"] == "Pennsylvania"
    assert results[0]["county_name"] == "Allegheny"
    assert results[0]["locality_name"] == "Pittsburgh"
