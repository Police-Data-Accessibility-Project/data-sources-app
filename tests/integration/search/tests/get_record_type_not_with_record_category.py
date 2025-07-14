from http import HTTPStatus

from middleware.enums import RecordTypes
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategoryEnum


def test_search_get_record_type_not_with_record_category(
    search_test_setup: SearchTestSetup,
):
    """
    The `record_type` parameter should not be provided if `record_category` is provided.
    If this occurs, an error should be returned
    """
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus

    tdc.request_validator.search(
        headers=tus.api_authorization_header,
        location_id=sts.location_id,
        record_categories=[RecordCategoryEnum.POLICE],
        record_types=[RecordTypes.ARREST_RECORDS],
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_schema=MessageSchema,
        expected_json_content={
            "message": "Only one of 'record_categories' or 'record_types' should be provided."
        },
    )
