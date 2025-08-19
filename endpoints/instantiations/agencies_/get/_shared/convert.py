from typing import Any, Optional

from db.helpers_.result_formatting import location_to_location_info
from db.models.implementations.core.agency.core import Agency


def agency_to_agency_dict(agency: Agency) -> dict[str, Any]:
    if agency.locations is not None and len(agency.locations) > 0:
        first_location = agency.locations[0]
    else:
        first_location = None

    return {
        "id": agency.id,
        "submitted_name": agency.name,
        "name": agency.name,
        "homepage_url": agency.homepage_url,
        "lat": None,
        "lng": None,
        "defunct_year": agency.defunct_year,
        "agency_type": agency.agency_type,
        "multi_agency": agency.multi_agency,
        "no_web_presence": agency.no_web_presence,
        "approval_status": agency.approval_status,
        "rejection_reason": agency.rejection_reason,
        "last_approval_editor": agency.last_approval_editor,
        "submitter_contact": agency.submitter_contact,
        "jurisdiction_type": agency.jurisdiction_type,
        "airtable_agency_last_modified": agency.airtable_agency_last_modified,
        "agency_created": agency.agency_created,
        "state_iso": first_location.state_iso if first_location else None,
        "state_name": first_location.state_name if first_location else None,
        "county_name": first_location.county_name if first_location else None,
        "county_fips": first_location.county_fips if first_location else None,
        "locality_name": first_location.locality_name if first_location else None,
    }


def agency_to_get_agencies_output(
    agency: Agency, requested_columns: Optional[list[str]] = None
) -> dict[str, Any]:
    if requested_columns is not None:
        d = {}
        for column in requested_columns:
            d[column] = getattr(agency, column)
    else:
        d = agency_to_agency_dict(agency)
    data_sources = []
    for data_source in agency.data_sources:
        data_sources.append(
            {
                "id": data_source.id,
                "name": data_source.name,
            }
        )
    d["data_sources"] = data_sources
    locations = []
    for location in agency.locations:
        locations.append(location_to_location_info(location))
    d["locations"] = locations
    return d
