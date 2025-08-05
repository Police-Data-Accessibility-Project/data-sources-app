from datetime import datetime, timezone, timedelta

from db.models.implementations.core.agency.core import Agency
from endpoints.schema_config.instantiations.agencies.post import AgenciesPostEndpointSchemaConfig
from middleware.enums import JurisdictionType
from tests.helpers.asserts import assert_contains_key_value_pairs
from tests.helpers.common_test_data import get_test_name
from tests.helpers.constants import AGENCIES_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_agencies_post(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    start_of_test_datetime = datetime.now(timezone.utc)
    # Test once with an existing locality, and once with a new locality

    tus_admin = tdc.get_admin_tus()

    def run_post(
        json: dict,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=AGENCIES_BASE_ENDPOINT,
            headers=tus_admin.jwt_authorization_header,
            json=json,
            expected_schema=AgenciesPostEndpointSchemaConfig.primary_output_schema,
        )

    def run_get(
        id_: str,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=f"{AGENCIES_BASE_ENDPOINT}/{id_}",
            headers=tus_admin.jwt_authorization_header,
        )

    # Test with a new locality
    data_to_post = tdc.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=get_test_name(),
    )
    json_data = run_post(data_to_post)
    id_ = json_data["id"]

    json_data = run_get(id_)

    agency_created = json_data["data"]["agency_created"]
    last_modified = json_data["data"]["airtable_agency_last_modified"]
    assert agency_created == last_modified, (
        "Agency created should be equal to last modified"
    )
    assert (
        # Within one minute to account for minor database/app discrepancies
        datetime.fromisoformat(agency_created) + timedelta(minutes=1)
        > start_of_test_datetime
    ), "Agency created should be after start of test"

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs={
            **data_to_post["agency_info"],
        },
    )
    # Check user id is correct
    agencies = tdc.db_client.get_all(Agency)
    assert len(agencies) == 1
    assert agencies[0]["creator_user_id"] == tus_admin.user_info.user_id

    # Test with a new locality
    data_to_post = test_data_creator_flask.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name="Capitola",
    )
    json_data = run_post(data_to_post)

    id_ = json_data["id"]

    json_data = run_get(id_)

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs={
            "name": data_to_post["agency_info"]["name"],
        },
    )
