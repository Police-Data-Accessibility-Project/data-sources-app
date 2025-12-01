from middleware.enums import JurisdictionType, AgencyType
from endpoints.instantiations.agencies_.post.dto import (
    AgenciesPostDTO,
    AgencyInfoPostDTO,
)


def test_get_typeahead_agencies(live_database_client, pittsburgh_id):
    # Insert test data into the database

    db_client = live_database_client
    _ = db_client.create_agency(
        dto=AgenciesPostDTO(
            agency_info=AgencyInfoPostDTO(
                name="Xylodammerung Police Agency",
                jurisdiction_type=JurisdictionType.STATE,
                agency_type=AgencyType.POLICE,
            ),
            location_ids=[pittsburgh_id],
        )
    )
    db_client.refresh_all_materialized_views()

    results = live_database_client.get_typeahead_agencies(search_term="Xyl", page=1)
    assert len(results) > 0
    assert results[0]["display_name"] == "Xylodammerung Police Agency"
    assert results[0]["jurisdiction_type"] == "state"
    assert results[0]["state_iso"] == "PA"
    assert results[0]["county_name"] == "Allegheny"
    assert results[0]["locality_name"] == "Pittsburgh"
