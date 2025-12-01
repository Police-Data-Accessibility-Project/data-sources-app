def test_get_typeahead_locations_county(live_database_client):
    results = live_database_client.get_typeahead_locations(search_term="All", page=1)
    assert len(results) > 0

    assert results[0]["display_name"] == "Allegheny, Pennsylvania"
    assert results[0]["type"] == "County"
    assert results[0]["state_name"] == "Pennsylvania"
    assert results[0]["county_name"] == "Allegheny"
    assert results[0]["locality_name"] is None
