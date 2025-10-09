from typing import Optional

from db.enums import LocationType
from endpoints.schema_config.instantiations.user.profile.recent_searches import (
    UserProfileRecentSearchesEndpointSchemaConfig,
)
from middleware.enums import OutputFormatEnum, JurisdictionSimplified
from middleware.util.csv import read_from_csv
from middleware.util.type_conversion import get_enum_values
from tests.helpers.constants import USER_PROFILE_RECENT_SEARCHES_ENDPOINT
from tests.integration.search.constants import TEST_STATE, TEST_COUNTY, TEST_LOCALITY
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategoryEnum


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
            record_categories=[RecordCategoryEnum.POLICE],
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
        expected_schema=UserProfileRecentSearchesEndpointSchemaConfig.primary_output_schema,
    )

    assert data["metadata"]["count"] == 1

    assert data["data"][0] == {
        "location_id": sts.location_id,
        "state_name": TEST_STATE,
        "county_name": TEST_COUNTY,
        "locality_name": TEST_LOCALITY,
        "location_type": LocationType.LOCALITY.value,
        "record_categories": [RecordCategoryEnum.POLICE.value],
    }
