from db.db_client_dataclasses import WhereMapping
from db.enums import LocationType
from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)


class MultiLocationSetup:
    def __init__(self, tdc: TestDataCreatorDBClient) -> None:
        self.tdc = tdc
        self.pittsburgh_id = self.tdc.locality(
            locality_name="Pittsburgh",
            county_name="Allegheny",
            state_iso="PA",
        )
        self.allegheny_county_id = self.get_location_id(
            {
                "state_iso": "PA",
                "county_name": "Allegheny",
                "type": LocationType.COUNTY,
            }
        )
        self.philadelphia_county_id = self.get_location_id(
            {
                "state_iso": "PA",
                "county_name": "Philadelphia",
                "type": LocationType.COUNTY,
            }
        )
        self.pennsylvania_id = self.get_location_id(
            {
                "state_iso": "PA",
                "type": LocationType.STATE,
            }
        )
        self.california_id = self.get_location_id(
            {
                "state_iso": "CA",
                "type": LocationType.STATE,
            }
        )
        self.orange_county_id = self.get_location_id(
            {
                "state_iso": "CA",
                "county_name": "Orange",
                "type": LocationType.COUNTY,
            }
        )
        self.orange_county_locality_id = self.tdc.locality(
            county_name="Orange", state_iso="CA"
        )
        self.tdc.db_client.update_location_by_id(
            location_id=self.pittsburgh_id,
            dto=LocationPutDTO(
                latitude=39.5,
                longitude=93.1,
            ),
        )
        self.tdc.db_client.refresh_all_materialized_views()

    def get_location_id(self, d: dict):
        return self.tdc.db_client.get_location_id(
            where_mappings=WhereMapping.from_dict(d)
        )
