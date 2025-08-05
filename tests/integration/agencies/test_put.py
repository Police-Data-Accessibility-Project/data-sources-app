"""Integration tests for /agencies endpoint"""

import time
from datetime import datetime

from endpoints.schema_config.instantiations.agencies.by_id.put import (
    AgenciesByIDPutEndpointSchemaConfig,
)
from middleware.enums import JurisdictionType
from endpoints.instantiations.agencies_.put.schemas.inner import (
    AgencyInfoPutSchema,
)

from tests.helpers.common_test_data import get_test_name
from tests.helpers.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.constants import AGENCIES_BASE_ENDPOINT

from tests.helpers.asserts import (
    assert_contains_key_value_pairs,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_agencies_put(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    data_to_post = tdc.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=get_test_name(),
    )

    admin_tus = tdc.get_admin_tus()

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json=data_to_post,
    )

    agency_id = json_data["id"]

    # Add sleep to allow update time to be distinct from creation time
    time.sleep(1)

    BY_ID_ENDPOINT = f"{AGENCIES_BASE_ENDPOINT}/{agency_id}"

    agency_info = generate_test_data_from_schema(
        schema=AgencyInfoPutSchema(),
        override={
            "jurisdiction_type": JurisdictionType.FEDERAL.value,
        },
    )

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=BY_ID_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json={"agency_info": agency_info},
        expected_schema=AgenciesByIDPutEndpointSchemaConfig.primary_output_schema,
    )

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=BY_ID_ENDPOINT,
        headers=admin_tus.api_authorization_header,
    )

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs=agency_info,
    )

    agency_created = json_data["data"]["agency_created"]
    last_modified = json_data["data"]["airtable_agency_last_modified"]
    assert datetime.fromisoformat(agency_created) < datetime.fromisoformat(
        last_modified
    )


