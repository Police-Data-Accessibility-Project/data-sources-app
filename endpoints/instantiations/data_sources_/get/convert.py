from typing import Any

from db.helpers_.result_formatting import location_to_location_info
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.models.implementations.core.location.expanded import LocationExpanded


def data_source_to_get_data_sources_output(
    data_source: DataSourceExpanded,
    data_sources_columns: list[str] = None,
    data_requests_columns: list[str] = None,
) -> dict[str, Any]:
    # Data source itself
    data_source_dict = {}
    for column in data_sources_columns:
        data_source_dict[column] = getattr(data_source, column)

    # Associated data requests
    data_requests = []
    for data_request in data_source.data_requests:
        data_request_dict = {}
        for column in data_requests_columns:
            data_request_dict[column] = getattr(data_request, column)
        data_requests.append(data_request_dict)
    data_source_dict["data_requests"] = data_requests

    # Associated agencies
    agencies = []
    for agency in data_source.agencies:
        if len(agency.locations) > 0:
            first_location: LocationExpanded = agency.locations[0]
        else:
            first_location: None = None

        # Agency
        agency_dict = {
            "id": agency.id,
            "name": agency.name,
            "submitted_name": agency.name,
            "jurisdiction_type": agency.jurisdiction_type,
            "agency_type": agency.agency_type,
            "state_iso": first_location.state_iso if first_location else None,
            "state_name": first_location.state_name if first_location else None,
            "county_name": first_location.county_name if first_location else None,
            "county_fips": first_location.county_fips if first_location else None,
            "locality_name": (first_location.locality_name if first_location else None),
        }

        # Agency Meta URLs
        meta_urls: list[str] = []
        for meta_url in agency.meta_urls:
            meta_urls.append(meta_url.source_url)
        agency_dict["meta_urls"] = meta_urls

        # Associated locations
        locations = []
        for location in agency.locations:
            locations.append(location_to_location_info(location))
        agency_dict["locations"] = locations

        agencies.append(agency_dict)
    data_source_dict["agencies"] = agencies

    return data_source_dict
