from db.db_client_dataclasses import WhereMapping
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema
from tests.helpers.common_test_data import get_test_name
from tests.helpers.constants import AGENCIES_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_agencies_delete(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json={
            "agency_info": {
                "name": get_test_name(),
                "jurisdiction_type": JurisdictionType.FEDERAL.value,
                "agency_type": AgencyType.COURT.value,
            }
        },
    )

    agency_id = json_data["id"]

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=f"{AGENCIES_BASE_ENDPOINT}/{agency_id}",
        headers=admin_tus.jwt_authorization_header,
        expected_schema=MessageSchema,
    )

    results = tdc.db_client._select_from_relation(
        relation_name="agencies",
        columns=["name"],
        where_mappings=[WhereMapping(column="id", value=int(agency_id))],
    )

    assert len(results) == 0
