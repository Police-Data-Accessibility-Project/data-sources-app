"""
Formats results for specific database queries
Coupled with the DatabaseClient class, whose outputs are formatted here
"""

from typing import Any

from db.enums import LocationType
from db.models.implementations.core.location.expanded import LocationExpanded


def location_to_location_info(location: LocationExpanded) -> dict[str, Any]:
    return {
        "type": location.type,
        "location_id": location.id,
        "state_iso": location.state_iso,
        "state_name": location.state_name,
        "county_name": location.county_name,
        "county_fips": location.county_fips,
        "locality_name": location.locality_name,
        "display_name": location.display_name,
    }


def get_expanded_display_name(location: LocationExpanded) -> str:
    loc_type = LocationType(location.type)
    match loc_type:
        case LocationType.STATE:
            return location.state_name
        case LocationType.COUNTY:
            return f"{location.county_name}, {location.state_name}"
        case LocationType.LOCALITY:
            return f"{location.locality_name}, {location.county_name}, {location.state_name}"


def get_display_name(
    location_type: LocationType,
    state_name: str | None,
    county_name: str | None,
    locality_name: str | None,
) -> str:
    match location_type:
        case LocationType.STATE:
            return state_name
        case LocationType.COUNTY:
            return f"{county_name}, {state_name}"
        case LocationType.LOCALITY:
            return f"{locality_name}, {county_name}, {state_name}"
        case LocationType.NATIONAL:
            return "United States - All"

    raise ValueError(f"Invalid location type: {location_type}")
