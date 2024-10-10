from http import HTTPStatus

from marshmallow import Schema

from conftest import test_data_creator_flask, monkeysession
from database_client.db_client_dataclasses import WhereMapping
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.constants import GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_github_data_requests_issues_post(test_data_creator_flask: TestDataCreatorFlask, monkeypatch):
    tdc = test_data_creator_flask

    # Mock `create_github_issue` to return a mock issue url
    mock_github_issue_url = "https://github.com/cool-github-issue-url"
    mock_create_github_issue = lambda *args, **kwargs: mock_github_issue_url
    monkeypatch.setattr(
        "middleware.primary_resource_logic.github_issue_app_logic.create_github_issue",
        mock_create_github_issue
    )

    # Create standard user
    tus = tdc.standard_user()

    # Create test data request
    cdr = tdc.data_request(tus)

    def call_endpoint(
            expected_response_status: HTTPStatus = HTTPStatus.OK,
            expected_schema: Schema = SchemaConfigs.GITHUB_DATA_REQUESTS_ISSUES_POST.value.output_schema,
            expected_json_content: dict = None,
            user_tus: TestUserSetup = tdc.get_admin_tus()
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT.format(
                data_request_id=cdr.id),
            headers=user_tus.jwt_authorization_header,
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content
        )
    # The user themselves should not be able to create an issue
    call_endpoint(
        user_tus=tus,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=MessageSchema(),
        expected_json_content={
            "message": "You do not have permission to access this endpoint"
        },
    )

    # Call endpoint and confirm it returns a mock issue url
    response_json = call_endpoint(
        expected_json_content={
            "message": "Issue created successfully",
            "github_issue_url": mock_github_issue_url
        }
    )

    github_issue_url = response_json["github_issue_url"]

    # Check database to confirm it is present
    result = tdc.db_client.get_data_requests(
        columns=["github_issue_url"],
        where_mappings=[WhereMapping(column="id", value=int(cdr.id))],
    )
    assert result[0]["github_issue_url"] == github_issue_url

    # Try to run again and confirm it is rejected, because it already exists
    call_endpoint(
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": f"Data Request already has an associated Github Issue.",
            "github_issue_url": github_issue_url
        },
    )




