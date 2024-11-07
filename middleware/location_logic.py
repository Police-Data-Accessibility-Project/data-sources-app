from dataclasses import asdict
from typing import Union

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType
from middleware.enums import Relations
from middleware.schema_and_dto_logic.common_schemas_and_dtos import LocationInfoDTO


class InvalidLocationError(Exception):
    pass


def get_location_id(
    db_client: DatabaseClient, location_info: Union[LocationInfoDTO, dict]
):
    if isinstance(location_info, dict):
        location_info_dict = location_info
        location_info = LocationInfoDTO(**location_info)
    else:
        location_info_dict = asdict(location_info)

    location_info_where_mappings = WhereMapping.from_dict(location_info_dict)
    # Get location id
    location_id = db_client.get_location_id(where_mappings=location_info_where_mappings)
    if location_id is not None:
        return location_id
    _raise_if_not_locality(location_info, location_info_dict)

    # In the case of a nonexistent locality, this can be added,
    # provided the rest of the location is valid
    county_id = _get_county_id(db_client, location_info_dict)

    # If this exists, locality does not yet exist in database and should be added. Add and return location id
    db_client.create_locality(
        column_value_mappings={
            "name": location_info.locality_name,
            "county_id": county_id,
        }
    )
    return db_client.get_location_id(where_mappings=location_info_where_mappings)


def _raise_if_not_locality(location_info, location_info_dict):
    if location_info.type != LocationType.LOCALITY:
        # Invalid location
        raise InvalidLocationError(f"{location_info_dict} is not a valid location")


def _get_county_id(db_client, location_info_dict) -> int:
    county_dict = {
        "county_fips": location_info_dict["county_fips"],
        "state_iso": location_info_dict["state_iso"],
        "type": LocationType.COUNTY,
    }
    results = db_client._select_from_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["county_id"],
        where_mappings=WhereMapping.from_dict(county_dict),
    )
    location_without_locality_exists = len(results) > 0
    if not location_without_locality_exists:
        raise InvalidLocationError(
            f"{location_info_dict} is not a valid location: {county_dict} is not a valid county"
        )
    return results[0]["county_id"]
