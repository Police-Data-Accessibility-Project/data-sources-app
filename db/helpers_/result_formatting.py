"""
Formats results for specific database queries
Coupled with the DatabaseClient class, whose outputs are formatted here
"""

from typing import Any, Optional

from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.inspection import inspect

from db.constants import (
    DATA_SOURCES_MAP_COLUMN,
    METADATA_METHOD_NAMES,
)
from db.enums import LocationType
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.models.implementations.core.location.expanded import LocationExpanded
from db.models.implementations.core.agency.core import Agency
from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from db.subquery_logic import SubqueryParameters
from utilities.common import format_arrays


def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
    return tuples_to_column_value_dict(DATA_SOURCES_MAP_COLUMN, results)


def format_with_metadata(
    data: list[dict],
    relation_name: str,
    subquery_parameters: Optional[list[SubqueryParameters]] = [],
) -> dict[str, Any]:
    metadata_dict = {}
    relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation_name]

    # Iterate through all properties of the Table
    for name, descriptor in inspect(relation_reference).all_orm_descriptors.items():
        # Retrieve and call the metadata method
        if type(descriptor) != hybrid_method or name not in METADATA_METHOD_NAMES:
            continue
        metadata_result = getattr(relation_reference, name)(
            data=data,
            subquery_parameters=subquery_parameters,
        )
        if metadata_result is not None:
            metadata_dict.update(metadata_result)

    return {
        "metadata": metadata_dict,
        "data": data,
    }


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
        "lat": agency.lat,
        "lng": agency.lng,
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


def agency_to_data_sources_get_related_agencies_output(
    agency: Agency,
):
    agency_dict = agency_to_agency_dict(agency)
    locations = []
    for location in agency.locations:
        location_dict = location_to_location_info(location)
        locations.append(location_dict)
    agency_dict["locations"] = locations
    return agency_dict


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
            first_location = agency.locations[0]
        else:
            first_location = None

        agency_dict = {
            "id": agency.id,
            "name": agency.name,
            "submitted_name": agency.name,
            "jurisdiction_type": agency.jurisdiction_type,
            "agency_type": agency.agency_type,
            "homepage_url": agency.homepage_url,
            "state_iso": first_location.state_iso if first_location else None,
            "state_name": first_location.state_name if first_location else None,
            "county_name": first_location.county_name if first_location else None,
            "county_fips": first_location.county_fips if first_location else None,
            "locality_name": (first_location.locality_name if first_location else None),
        }
        # Associated locations
        locations = []
        for location in agency.locations:
            locations.append(location_to_location_info(location))
        agency_dict["locations"] = locations
        agencies.append(agency_dict)
    data_source_dict["agencies"] = agencies

    return data_source_dict


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


def tuples_to_column_value_dict(columns: list[str], tuples: list[tuple]) -> list[dict]:
    """
    Combine a list of output columns with a list of results,
    and produce a list of dictionaries where the keys correspond
    to the output columns and the values correspond to the results
    :param columns:
    :param tuples:
    :return:
    """
    zipped_results = [dict(zip(columns, result)) for result in tuples]
    formatted_results = []
    for zipped_result in zipped_results:
        formatted_results.append(format_arrays(zipped_result))
    return formatted_results


def get_display_name(
    location_type: LocationType,
    state_name: Optional[str],
    county_name: Optional[str],
    locality_name: Optional[str],
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
