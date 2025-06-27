from db.enums import RequestStatus
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from middleware.enums import RecordTypes
from middleware.third_party_interaction_logic.github.issue_info import GithubIssueInfo
from middleware.third_party_interaction_logic.github.issue_project_info.core import (
    GithubIssueProjectInfo,
)
from middleware.third_party_interaction_logic.github.issue_project_info.model import (
    GIPIInfo,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.integration.github_data_requests_issues.constants import PATCH_ROOT
from tests.integration.github_data_requests_issues.happy_path.manager import (
    TestSynchronizeGithubIssueHappyPathManager,
)
from tests.integration.test_check_database_health import wipe_database


def test_synchronize_github_issue(
    test_data_creator_flask: TestDataCreatorFlask,
    monkeypatch,
):
    manager = TestSynchronizeGithubIssueHappyPathManager(
        test_data_creator_flask, monkeypatch_=monkeypatch
    )

    # Sync 1: No data requests created; no issues created
    manager.sync()

    # Confirm the presence of no data requests and no data request github info
    manager.assert_number_of_data_requests(0)
    manager.assert_length_of_github_issue_infos(0)
    assert manager.mock_issue_count == 0

    # Sync 2: Create 3 Issues in the database, mark 2 as 'Ready to Start', 1 as 'Complete'
    # Check that 2 github issues are created for the 2 marked 'Ready to Start'
    data_request_ids = manager.setup_for_sync_2()
    manager.check_sync_2(data_request_ids)

    # Sync 3: Create 1 Issue in the database, mark 1 as 'Ready to Start', update existing Github Issue
    # Check that 1 github issue is created, and the existing issue is updated in the database
    manager.setup_for_sync_3(data_request_ids)
    manager.check_sync_3(data_request_ids)

    # Sync 4: Do nothing
    # Check that no github issues are created, no data updated
    manager.check_sync_4()
