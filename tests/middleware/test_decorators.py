from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus
from pytest_mock import mocker

from middleware.access_logic import AccessInfo
from middleware.decorators import (
    api_key_required,
    permissions_required,
    api_key_or_jwt_required,
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


def test_permissions_required(dummy_permissions_required_route, monkeypatch):
    mock_check_permissions = MagicMock()
    monkeypatch.setattr(
        "middleware.decorators.check_permissions", mock_check_permissions
    )

    dummy_permissions_required_route()
    mock_check_permissions.assert_called_once_with(PermissionsEnum.READ_ALL_USER_INFO)


def test_api_key_or_jwt_required(monkeypatch):
    mock_get_access_info = MagicMock()
    monkeypatch.setattr(
        "middleware.decorators.get_access_info_from_jwt_or_api_key",
        mock_get_access_info,
    )
    mock_get_access_info.return_value = AccessInfo(
        user_email="test_user",
        access_type=AccessTypeEnum.JWT,
        permissions=[PermissionsEnum.READ_ALL_USER_INFO, PermissionsEnum.DB_WRITE],
    )

    # Create a simple function to decorate
    @api_key_or_jwt_required
    def sample_function(access_info: AccessInfo):
        return access_info

    # Call the decorated function
    assert sample_function() == mock_get_access_info.return_value
