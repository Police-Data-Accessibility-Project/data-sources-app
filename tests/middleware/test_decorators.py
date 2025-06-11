from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus

from middleware.decorators.api_key_required import api_key_required


@pytest.fixture
def dummy_api_key_required_route():
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


def test_api_key_required(dummy_api_key_required_route, monkeypatch):
    # Mock the check_api_key function
    mock_check_api_key = MagicMock()
    monkeypatch.setattr(
        "middleware.decorators.api_key_required.check_api_key", mock_check_api_key
    )

    # Create a simple function to decorate
    @api_key_required
    def sample_function():
        return "Protected Resource"

    # Call the decorated function
    result = sample_function()

    # Assert that check_api_key was called
    mock_check_api_key.assert_called_once()

    # Assert that the decorated function returns the correct value
    assert result == "Protected Resource"
