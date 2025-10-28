from db.enums import RequestStatus
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from middleware.enums import RecordTypesEnum
from middleware.third_party_interaction_logic.github.issue_info import GithubIssueInfo
from middleware.third_party_interaction_logic.github.issue_project_info.core import (
    GithubIssueProjectInfo,
)
from middleware.third_party_interaction_logic.github.issue_project_info.model import (
    GIPIInfo,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.integration.github_data_requests_issues.constants import PATCH_ROOT


class TestSynchronizeGithubIssueHappyPathManager:
    def __init__(self, tdc: TestDataCreatorFlask, monkeypatch_):
        self.tdc = tdc
        self.tdc.clear_test_data()
        self.db_client = tdc.db_client
        self.mock_issue_count = 0
        self.mock_repo: dict[int, GIPIInfo] = {}
        self.create_mock_github_issue_manager(monkeypatch_)
        self.create_mock_get_github_issue_project_statuses(monkeypatch_)

    def create_mock_github_issue_manager(self, monkeypatch_):
        def increment_issue_count():
            self.mock_issue_count += 1

        def get_mock_issue_count():
            return self.mock_issue_count

        def set_gipi_info(issue_count: int, gipi_info: GIPIInfo):
            self.mock_repo[issue_count] = gipi_info

        class MockGithubIssueManager:
            # Mock create GitHub Issue
            def create_issue_with_status(
                self, title: str, body: str, status: RequestStatus, record_types: list
            ) -> GithubIssueInfo:
                # Create mock github issue with status "Ready to Start"
                increment_issue_count()
                issue_count = get_mock_issue_count()
                gipi_info = GIPIInfo(
                    project_status=status.value, record_types=record_types
                )
                set_gipi_info(issue_count, gipi_info=gipi_info)
                return GithubIssueInfo(
                    id="mock_github_issue_id",
                    url=f"https://github.com/cool-github-issue-url/{issue_count}",
                    number=issue_count,
                )

        monkeypatch_.setattr(
            f"{PATCH_ROOT}.GithubIssueManager",
            MockGithubIssueManager,
        )

    def create_mock_get_github_issue_project_statuses(self, monkeypatch_):
        def mock_get_github_issue_project_statuses(
            issue_numbers: list[int],
        ) -> GithubIssueProjectInfo:
            gipi = GithubIssueProjectInfo()
            for issue_number in issue_numbers:
                gipi.add_info(issue_number, self.mock_repo[issue_number])
            return gipi

        # Patch `git_github_issue_project_statuses` to return the mock
        monkeypatch_.setattr(
            f"{PATCH_ROOT}.get_github_issue_project_statuses",
            mock_get_github_issue_project_statuses,
        )

    def assert_number_of_data_requests(self, count: int):
        assert len(self.db_client.get_all(DataRequest)) == count

    def assert_length_of_github_issue_infos(self, count: int):
        assert len(self.db_client.get_all(DataRequestsGithubIssueInfo)) == count

    def sync(
        self,
        expected_message="Added 0 data requests to GitHub. Updated 0 data requests in database.",
        expected_issues_created=None,
    ):
        if expected_issues_created is None:
            expected_issues_created = []

        content = self.tdc.request_validator.github_data_requests_issues_synchronize(
            headers=self.tdc.get_admin_tus().jwt_authorization_header,
        )
        expected_issues_created = sorted(
            expected_issues_created, key=lambda x: x["data_request_id"]
        )
        issues_created = sorted(
            content["issues_created"], key=lambda x: x["data_request_id"]
        )
        assert content["message"] == expected_message
        assert issues_created == expected_issues_created

    def setup_for_sync_2(self) -> list[int]:
        data_request_ids = []
        for i in range(3):
            data_request_id = self.db_client.create_data_request(
                column_value_mappings={
                    "title": f"Data Request {i}",
                    "request_status": "Ready to start" if i < 2 else "Complete",
                    "submission_notes": f"Submission Notes {i}",
                    "data_requirements": f"Data Requirements {i}",
                }
            )
            data_request_ids.append(data_request_id)
            # Link to location
            self.db_client.create_request_location_relation(
                column_value_mappings={
                    "data_request_id": data_request_id,
                    "location_id": 1,
                }
            )
        return data_request_ids

    def check_sync_2(self, data_request_ids: list[int]):
        self.sync(
            expected_message="Added 2 data requests to GitHub. Updated 0 data requests in database.",
            expected_issues_created=[
                {
                    "data_request_id": data_request_ids[0],
                    "github_issue_url": "https://github.com/cool-github-issue-url/1",
                },
                {
                    "data_request_id": data_request_ids[1],
                    "github_issue_url": "https://github.com/cool-github-issue-url/2",
                },
            ],
        )

        # Check that 2 github issues are created for the 2 marked 'Ready to Start'
        assert self.mock_issue_count == 2
        assert list(self.mock_repo.values()) == [
            GIPIInfo(project_status="Ready to start", record_types=[]),
            GIPIInfo(project_status="Ready to start", record_types=[]),
        ]

        # Confirm the presence of 3 data requests and 2 data request github info
        self.assert_number_of_data_requests(3)
        self.assert_length_of_github_issue_infos(2)

    def setup_for_sync_3(self, data_request_ids: list[int]):
        data_request_id = self.db_client.create_data_request(
            column_value_mappings={
                "title": "Data Request 3",
                "request_status": "Ready to start",
                "submission_notes": "Submission Notes 3",
                "data_requirements": "Data Requirements 3",
                "record_types_required": [
                    "Dispatch Recordings",
                    "Incarceration Records",
                ],
            }
        )
        data_request_ids.append(data_request_id)
        # Update existing issue to "Complete"
        self.mock_repo[1] = GIPIInfo(
            project_status="Complete", record_types=[RecordTypesEnum.RECORDS_REQUEST_INFO]
        )

    def check_sync_3(self, data_request_ids: list[int]):
        self.sync(
            expected_message="Added 1 data requests to GitHub. Updated 1 data requests in database.",
            expected_issues_created=[
                {
                    "data_request_id": data_request_ids[3],
                    "github_issue_url": "https://github.com/cool-github-issue-url/3",
                },
            ],
        )
        assert self.mock_issue_count == 3
        assert list(self.mock_repo.values()) == [
            GIPIInfo(
                project_status="Complete",
                record_types=[RecordTypesEnum.RECORDS_REQUEST_INFO],
            ),
            GIPIInfo(project_status="Ready to start", record_types=[]),
            GIPIInfo(
                project_status="Ready to start",
                record_types=[
                    RecordTypesEnum.DISPATCH_RECORDINGS,
                    RecordTypesEnum.INCARCERATION_RECORDS,
                ],
            ),
        ]

        # Confirm the presence of 4 data requests and 3 data request github info
        self.assert_number_of_data_requests(4)
        self.assert_length_of_github_issue_infos(3)

    def check_sync_4(self):
        self.sync()

        # Confirm the presence of 4 data requests and 3 data request github info
        assert self.mock_issue_count == 3
        assert list(self.mock_repo.values()) == [
            GIPIInfo(
                project_status="Complete",
                record_types=[RecordTypesEnum.RECORDS_REQUEST_INFO],
            ),
            GIPIInfo(project_status="Ready to start", record_types=[]),
            GIPIInfo(
                project_status="Ready to start",
                record_types=[
                    RecordTypesEnum.DISPATCH_RECORDINGS,
                    RecordTypesEnum.INCARCERATION_RECORDS,
                ],
            ),
        ]

        self.assert_number_of_data_requests(4)
        self.assert_length_of_github_issue_infos(3)
