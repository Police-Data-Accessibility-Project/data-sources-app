from db.helpers_.result_formatting import location_to_location_info
from db.models.implementations.core.agency.core import Agency
from endpoints.instantiations.agencies_.get._shared.convert import (
    agency_to_agency_dict,
    agency_to_meta_urls,
)


def agency_to_data_sources_get_related_agencies_output(
    agency: Agency,
):
    agency_dict = agency_to_agency_dict(agency)

    locations = []
    for location in agency.locations:
        location_dict = location_to_location_info(location)
        locations.append(location_dict)
    agency_dict["locations"] = locations

    # Meta URLs
    meta_urls = agency_to_meta_urls(agency)
    agency_dict["meta_urls"] = meta_urls

    return agency_dict
