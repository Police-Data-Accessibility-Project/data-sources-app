from typing import Optional

from db.enums import LocationType
from endpoints.schema_config.enums import SchemaConfigs
from middleware.enums import OutputFormatEnum, JurisdictionSimplified
from middleware.util.csv import read_from_csv
from middleware.util.type_conversion import get_enum_values
from tests.helper_scripts.constants import USER_PROFILE_RECENT_SEARCHES_ENDPOINT
from tests.integration.search.constants import TEST_STATE, TEST_COUNTY, TEST_LOCALITY
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategories


def test_search_get(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus
    tdcdb = tdc.tdcdb

    tdcdb.link_data_source_to_agency(
        data_source_id=tdcdb.data_source().id,
        agency_id=tdcdb.agency(location_id=sts.location_id).id,
    )

    def search(record_format: Optional[OutputFormatEnum] = OutputFormatEnum.JSON):
        return tdc.request_validator.search(
            headers=tus.api_authorization_header,
            location_id=sts.location_id,
            record_categories=[RecordCategories.POLICE],
            format=record_format,
        )

    json_data = search()
    assert json_data["count"] > 0

    jurisdiction_count = 0
    jurisdictions = get_enum_values(JurisdictionSimplified)
    for jurisdiction in jurisdictions:
        jurisdiction_count += json_data["data"][jurisdiction]["count"]

    assert jurisdiction_count == json_data["count"]

    # Check that search shows up in user's recent searches
    data = tdc.request_validator.get(
        endpoint=USER_PROFILE_RECENT_SEARCHES_ENDPOINT,
        headers=tus.jwt_authorization_header,
        expected_schema=SchemaConfigs.USER_PROFILE_RECENT_SEARCHES.value.primary_output_schema,
    )

    assert data["metadata"]["count"] == 1

    assert data["data"][0] == {
        "location_id": sts.location_id,
        "state_name": TEST_STATE,
        "county_name": TEST_COUNTY,
        "locality_name": TEST_LOCALITY,
        "location_type": LocationType.LOCALITY.value,
        "record_categories": [RecordCategories.POLICE.value],
    }

    csv_data = search(record_format=OutputFormatEnum.CSV)

    results = read_from_csv(csv_data)

    assert len(results) == json_data["count"]

    # Flatten json data for comparison
    flat_json_data = []
    for jurisdiction in jurisdictions:
        if json_data["data"][jurisdiction]["count"] == 0:
            continue
        for result in json_data["data"][jurisdiction]["results"]:
            flat_json_data.append(result)

    # Sort both the flat json data and the csv results for comparison
    # Due to differences in how CSV and JSON results are formatted, compare only ids
    json_ids = sorted([result["id"] for result in flat_json_data])
    csv_ids = sorted(
        [int(result["id"]) for result in results]
    )  # CSV ids are formatted as strings

    assert json_ids == csv_ids
