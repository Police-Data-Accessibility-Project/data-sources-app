from http import HTTPStatus

from marshmallow import Schema

from conftest import test_data_creator_flask, monkeysession
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RequestStatus
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.third_party_interaction_logic.github_issue_api_logic import (
    GithubIssueInfo,
    GithubIssueProjectInfo,
)
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import (
    TestDataCreatorFlask,
    get_random_number_for_testing,
)
from tests.helper_scripts.constants import (
    GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT,
    DATA_REQUESTS_BY_ID_ENDPOINT,
    GITHUB_DATA_REQUESTS_SYNCHRONIZE,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.conftest import clear_data_requests, dev_db_client

PATCH_ROOT = "middleware.primary_resource_logic.github_issue_app_logic"


def generate_fake_github_issue_info() -> GithubIssueInfo:
    number = get_random_number_for_testing()
    return GithubIssueInfo(
        url=f"https://github.com/cool-github-issue-url/{number}", number=number
    )


def test_github_data_requests_issues_post(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    tdc = test_data_creator_flask

    # Mock `create_github_issue` to return a mock issue url
    fake_github_issue_info = generate_fake_github_issue_info()
    mock_github_issue_url = fake_github_issue_info.url
    mock_create_github_issue = lambda *args, **kwargs: GithubIssueInfo(
        url=mock_github_issue_url, number=fake_github_issue_info.number
    )
    monkeypatch.setattr(f"{PATCH_ROOT}.create_github_issue", mock_create_github_issue)

    # Create standard user
    tus = tdc.standard_user()

    # Create test data request
    cdr = tdc.data_request(tus)

    def call_endpoint(
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema: Schema = SchemaConfigs.GITHUB_DATA_REQUESTS_ISSUES_POST.value.primary_output_schema,
        expected_json_content: dict = None,
        user_tus: TestUserSetup = tdc.get_admin_tus(),
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT.format(
                data_request_id=cdr.id
            ),
            headers=user_tus.jwt_authorization_header,
            expected_schema=expected_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
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
            "github_issue_url": mock_github_issue_url,
        }
    )

    github_issue_url = response_json["github_issue_url"]

    # TODO: Modify so that this is done via a GET request
    # Check database to confirm it is present
    result = tdc.db_client.get_data_requests(
        columns=["github_issue_url", "github_issue_number"],
        where_mappings=[WhereMapping(column="id", value=int(cdr.id))],
    )
    assert result[0]["github_issue_url"] == github_issue_url
    # Check that the issue number is present and aligns with the issue url
    assert result[0]["github_issue_number"] == int(github_issue_url.split("/")[-1])

    # Try to run again and confirm it is rejected, because it already exists
    call_endpoint(
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": f"Data Request already has an associated Github Issue.",
            "github_issue_url": github_issue_url,
        },
    )


def test_synchronize_github_issue(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch, clear_data_requests
):

    tdc = test_data_creator_flask

    def update_data_request(
        data_request_id: int,
        request_status: RequestStatus,
    ):
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="put",
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=tdc.get_admin_tus().jwt_authorization_header,
            json={
                "entry_data": {"request_status": request_status.value},
            },
        )
        # Use post requests to update the request status

    def add_fake_github_info_for_data_request(data_request_id: int) -> GithubIssueInfo:
        fake_github_info = generate_fake_github_issue_info()
        # Directly update the database with the github info
        tdc.db_client.create_data_request_github_info(
            column_value_mappings={
                "data_request_id": data_request_id,
                "github_issue_url": fake_github_info.url,
                "github_issue_number": fake_github_info.number,
            }
        )

        return fake_github_info

    # Create standard user
    tus = test_data_creator_flask.standard_user()

    # Add 3 data requests, 2 corresponding to these issues
    # The 3rd data request should be listed as archived.
    dr1 = tdc.data_request(tus)
    dr2 = tdc.data_request(tus)
    dr3 = tdc.data_request(tus)

    # Update data requests to required statuses
    update_data_request(data_request_id=dr1.id, request_status=RequestStatus.ACTIVE)
    update_data_request(data_request_id=dr2.id, request_status=RequestStatus.ACTIVE)
    update_data_request(data_request_id=dr3.id, request_status=RequestStatus.ARCHIVED)

    # Add github info for data requests
    fgi_1 = add_fake_github_info_for_data_request(data_request_id=dr1.id)
    fgi_2 = add_fake_github_info_for_data_request(data_request_id=dr2.id)
    fgi_3 = add_fake_github_info_for_data_request(data_request_id=dr3.id)

    # Create GithubIssueProjectInfo with mock information
    gipi = GithubIssueProjectInfo()
    gipi.add_project_status(
        issue_number=fgi_1.number, project_status=RequestStatus.ACTIVE.value
    )
    gipi.add_project_status(
        issue_number=fgi_2.number, project_status=RequestStatus.COMPLETE.value
    )  # This one will yield a db update

    # Create a mock version of `get_github_issue_project_statuses` which validates the proper values are received
    # and returns the mock GithubIssueProjectInfo
    def mock_get_github_issue_project_statuses(
        issue_numbers: list[int],
    ) -> GithubIssueProjectInfo:
        assert issue_numbers == [
            fgi_1.number,
            fgi_2.number,
        ], f"Unexpected issue number in {issue_numbers}; expected only {fgi_1.number} and {fgi_2.number}"
        return gipi

    # Patch `git_github_issue_project_statuses` to return the mock
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_github_issue_project_statuses",
        mock_get_github_issue_project_statuses,
    )

    def call_endpoint(
        tus: TestUserSetup = tdc.get_admin_tus(),
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=GITHUB_DATA_REQUESTS_SYNCHRONIZE,
            headers=tus.jwt_authorization_header,
            expected_response_status=expected_response_status,
        )

    # Confirm a standard user cannot call the endpoint
    call_endpoint(
        tus=tdc.standard_user(), expected_response_status=HTTPStatus.FORBIDDEN
    )

    # Call the synchronize endpoint
    call_endpoint()

    # Confirm the data requests have been updated
    def check_data_request_github_info(
        data_request_id: int,
        github_issue_url: str,
        github_issue_number: int,
        expected_status: RequestStatus,
    ):
        response_json = run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=tdc.get_admin_tus().jwt_authorization_header,
        )
        assert response_json["data"]["github_issue_url"] == github_issue_url
        assert response_json["data"]["github_issue_number"] == github_issue_number
        assert response_json["data"]["request_status"] == expected_status.value

    check_data_request_github_info(
        data_request_id=dr1.id,
        github_issue_url=fgi_1.url,
        github_issue_number=fgi_1.number,
        expected_status=RequestStatus.ACTIVE,
    )
    check_data_request_github_info(
        data_request_id=dr2.id,
        github_issue_url=fgi_2.url,
        github_issue_number=fgi_2.number,
        expected_status=RequestStatus.COMPLETE,
    )
    check_data_request_github_info(
        data_request_id=dr3.id,
        github_issue_url=fgi_3.url,
        github_issue_number=fgi_3.number,
        expected_status=RequestStatus.ARCHIVED,
    )
