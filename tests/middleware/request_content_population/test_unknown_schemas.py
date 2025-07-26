from http import HTTPStatus

from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_unknown_schemas(test_data_creator_flask: TestDataCreatorFlask):
    """If a schema is submitted with values that are not in the schema, it should raise a ValidationError"""
    tdc = test_data_creator_flask
    rv = test_data_creator_flask.request_validator
    rv.get(
        endpoint="/api/typeahead/locations",
        headers=tdc.admin_tus.jwt_authorization_header,
        query_parameters={
            "query": "abc",
            "unknown": "abc"
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

