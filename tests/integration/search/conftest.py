import pytest

from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.integration.search.constants import TEST_LOCALITY, TEST_STATE, TEST_COUNTY
from tests.integration.search.search_test_setup import SearchTestSetup
from tests.integration.test_check_database_health import wipe_database


@pytest.fixture
def search_test_setup(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    wipe_database(tdc.db_client)

    try:
        tdc.locality(TEST_LOCALITY)
    except Exception:
        pass
    return SearchTestSetup(
        tdc=tdc,
        location_id=tdc.db_client.get_location_id(
            where_mappings={
                "state_name": TEST_STATE,
                "county_name": TEST_COUNTY,
                "locality_name": TEST_LOCALITY,
            }
        ),
        tus=tdc.standard_user(),
    )
