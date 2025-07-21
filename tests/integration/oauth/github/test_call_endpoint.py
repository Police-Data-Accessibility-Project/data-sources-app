from unittest.mock import MagicMock

from middleware.schema_and_dto.dtos.github.oauth import GithubOAuthRequestDTO
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)

PATCH_ROOT = "endpoints.instantiations.oauth_.oauth"


def test_call_endpoint(monkeypatch, test_data_creator_flask: TestDataCreatorFlask):
    """Test that a basic call to the endpoint runs without error."""

    # Set up mocks
    mock_setup_callback_session = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.setup_callback_session", mock_setup_callback_session
    )

    mock_populate_dto_with_request_content = MagicMock(
        return_value=GithubOAuthRequestDTO(redirect_url="https://test.com")
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.populate_dto_with_request_content",
        mock_populate_dto_with_request_content,
    )

    mock_redirect_to_github_authorization = MagicMock(return_value={})
    monkeypatch.setattr(
        f"{PATCH_ROOT}.redirect_to_github_authorization",
        mock_redirect_to_github_authorization,
    )
    # Call endpoint
    test_data_creator_flask.request_validator.get(endpoint="/api/oauth/github")

    # Assertions
    mock_setup_callback_session.assert_called_once()
    mock_populate_dto_with_request_content.assert_called_once()
    mock_redirect_to_github_authorization.assert_called_once()
