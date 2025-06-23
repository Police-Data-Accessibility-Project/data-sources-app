from http import HTTPStatus

from pydantic import BaseModel

from db.enums import RequestStatus
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from db.models.implementations.core.data_request.core import DataRequest
from middleware.enums import PermissionsEnum, RecordTypes
from middleware.third_party_interaction_logic.github.issue_info import GithubIssueInfo
from middleware.third_party_interaction_logic.github.issue_project_info.core import (
    GithubIssueProjectInfo,
)
from middleware.third_party_interaction_logic.github.issue_project_info.model import (
    GIPIInfo,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_functions_complex import create_test_user_setup
from tests.integration.test_check_database_health import wipe_database

PATCH_ROOT = "middleware.primary_resource_logic.github_issue_app"


class SynchronizeTestInfo(BaseModel):
    data_request_id: int
    github_issue_info: GithubIssueInfo


def test_synchronize_github_issue_denied(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch, clear_data_requests
):
    # Give a user every permission except github_sync
    tdc = test_data_creator_flask
    tus = create_test_user_setup(
        tdc.flask_client,
        permissions=[
            permission
            for permission in PermissionsEnum
            if permission != PermissionsEnum.GITHUB_SYNC
        ],
    )
    return tdc.request_validator.github_data_requests_issues_synchronize(
        headers=tus.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_synchronize_github_issue(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch, clear_data_requests
):

    tdc = test_data_creator_flask
    wipe_database(tdc.db_client)

    # Mock GitHub repo -- a simple dictionary of issue number to project status
    mock_issue_count = 0
    mock_repo: dict[int, GIPIInfo] = {}

    class MockGithubIssueManager:

        # Mock create GitHub Issue
        def create_issue_with_status(
            self, title: str, body: str, status: RequestStatus, record_types: list
        ) -> GithubIssueInfo:
            # Create mock github issue with status "Ready to Start"
            nonlocal mock_issue_count
            mock_issue_count += 1
            issue_count = mock_issue_count
            gipi_info = GIPIInfo(project_status=status.value, record_types=record_types)
            mock_repo[issue_count] = gipi_info
            return GithubIssueInfo(
                id="mock_github_issue_id",
                url=f"https://github.com/cool-github-issue-url/{issue_count}",
                number=issue_count,
            )

    monkeypatch.setattr(
        f"{PATCH_ROOT}.GithubIssueManager",
        MockGithubIssueManager,
    )

    def mock_get_github_issue_project_statuses(
        issue_numbers: list[int],
    ) -> GithubIssueProjectInfo:

        gipi = GithubIssueProjectInfo()
        for issue_number in issue_numbers:
            gipi.add_info(issue_number, mock_repo[issue_number])
        return gipi

    # Patch `git_github_issue_project_statuses` to return the mock
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_github_issue_project_statuses",
        mock_get_github_issue_project_statuses,
    )

    def sync(expected_json_content=None):
        if expected_json_content is None:
            expected_json_content = {
                "message": "Added 0 data requests to GitHub. Updated 0 data requests in database.",
                "issues_created": [],
            }
        return tdc.request_validator.github_data_requests_issues_synchronize(
            headers=tdc.get_admin_tus().jwt_authorization_header,
            expected_json_content=expected_json_content,
        )

    def get_all_data_requests():
        return tdc.db_client.get_all(DataRequest)

    def get_all_data_request_github_issue_infos():
        return tdc.db_client.get_all(DataRequestsGithubIssueInfo)

    # Sync 1: No data requests created; no issues created
    sync()

    # Confirm the presence of no data requests and no data request github info
    assert len(get_all_data_requests()) == 0
    assert len(get_all_data_request_github_issue_infos()) == 0
    assert mock_issue_count == 0

    # Sync 2: Create 3 Issues in the database, mark 2 as 'Ready to Start', 1 as 'Complete'
    # Check that 2 github issues are created for the 2 marked 'Ready to Start'
    data_request_ids = []
    for i in range(3):
        data_request_id = tdc.db_client.create_data_request(
            column_value_mappings={
                "title": f"Data Request {i}",
                "request_status": "Ready to start" if i < 2 else "Complete",
                "submission_notes": f"Submission Notes {i}",
                "data_requirements": f"Data Requirements {i}",
            }
        )
        data_request_ids.append(data_request_id)
        # Link to location
        tdc.db_client.create_request_location_relation(
            column_value_mappings={"data_request_id": data_request_id, "location_id": 1}
        )
    sync(
        expected_json_content={
            "message": "Added 2 data requests to GitHub. Updated 0 data requests in database.",
            "issues_created": [
                {
                    "data_request_id": data_request_ids[0],
                    "github_issue_url": "https://github.com/cool-github-issue-url/1",
                },
                {
                    "data_request_id": data_request_ids[1],
                    "github_issue_url": "https://github.com/cool-github-issue-url/2",
                },
            ],
        }
    )

    # Check that 2 github issues are created for the 2 marked 'Ready to Start'
    assert mock_issue_count == 2
    assert list(mock_repo.values()) == [
        GIPIInfo(project_status="Ready to start", record_types=[]),
        GIPIInfo(project_status="Ready to start", record_types=[]),
    ]

    # Confirm the presence of 3 data requests and 2 data request github info
    assert len(get_all_data_requests()) == 3
    assert len(get_all_data_request_github_issue_infos()) == 2

    # Sync 3: Create 1 Issue in the database, mark 1 as 'Ready to Start', update existing Github Issue
    # Check that 1 github issue is created, and the existing issue is updated in the database

    data_request_id = tdc.db_client.create_data_request(
        column_value_mappings={
            "title": "Data Request 3",
            "request_status": "Ready to start",
            "submission_notes": "Submission Notes 3",
            "data_requirements": "Data Requirements 3",
            "record_types_required": ["Dispatch Recordings", "Incarceration Records"],
        }
    )
    data_request_ids.append(data_request_id)
    # Update existing issue to "Complete"
    mock_repo[1] = GIPIInfo(
        project_status="Complete", record_types=[RecordTypes.RECORDS_REQUEST_INFO]
    )
    sync(
        expected_json_content={
            "message": "Added 1 data requests to GitHub. Updated 1 data requests in database.",
            "issues_created": [
                {
                    "data_request_id": data_request_ids[3],
                    "github_issue_url": "https://github.com/cool-github-issue-url/3",
                },
            ],
        }
    )
    assert mock_issue_count == 3
    assert list(mock_repo.values()) == [
        GIPIInfo(
            project_status="Complete", record_types=[RecordTypes.RECORDS_REQUEST_INFO]
        ),
        GIPIInfo(project_status="Ready to start", record_types=[]),
        GIPIInfo(
            project_status="Ready to start",
            record_types=[
                RecordTypes.DISPATCH_RECORDINGS,
                RecordTypes.INCARCERATION_RECORDS,
            ],
        ),
    ]

    # Confirm the presence of 4 data requests and 3 data request github info
    assert len(get_all_data_requests()) == 4
    assert len(get_all_data_request_github_issue_infos()) == 3

    # Get the modified data request and confirm the status in the database is updated

    # Sync 4: Do nothing
    # Check that no github issues are created, no data updated

    sync(
        expected_json_content={
            "message": "Added 0 data requests to GitHub. Updated 0 data requests in database.",
            "issues_created": [],
        }
    )

    # Confirm the presence of 4 data requests and 3 data request github info
    assert mock_issue_count == 3
    assert list(mock_repo.values()) == [
        GIPIInfo(
            project_status="Complete", record_types=[RecordTypes.RECORDS_REQUEST_INFO]
        ),
        GIPIInfo(project_status="Ready to start", record_types=[]),
        GIPIInfo(
            project_status="Ready to start",
            record_types=[
                RecordTypes.DISPATCH_RECORDINGS,
                RecordTypes.INCARCERATION_RECORDS,
            ],
        ),
    ]

    assert len(get_all_data_requests()) == 4
    assert len(get_all_data_request_github_issue_infos()) == 3
