from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus
from pytest_mock import mocker

from middleware.access_logic import AccessInfo
from middleware.decorators import (
    api_key_required,
    permissions_required,
    authentication_required,
)
from middleware.enums import PermissionsEnum, AccessTypeEnum


@pytest.fixture
def dummy_api_key_required_route():
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


def test_api_key_required(dummy_api_key_required_route, monkeypatch):
    # Mock the check_api_key function
    mock_check_api_key = MagicMock()
    monkeypatch.setattr("middleware.decorators.check_api_key", mock_check_api_key)

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


@pytest.fixture
def dummy_permissions_required_route():
    @permissions_required(PermissionsEnum.READ_ALL_USER_INFO)
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


@pytest.fixture
def dummy_authentication_required_route():
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY],
        restrict_to_permissions=[PermissionsEnum.READ_ALL_USER_INFO],
    )
    def _dummy_route(access_info: AccessInfo):
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


def test_permissions_required(dummy_permissions_required_route, monkeypatch):
    mock_check_permissions = MagicMock()
    monkeypatch.setattr(
        "middleware.decorators.check_permissions", mock_check_permissions
    )

    dummy_permissions_required_route()
    mock_check_permissions.assert_called_once_with(PermissionsEnum.READ_ALL_USER_INFO)

