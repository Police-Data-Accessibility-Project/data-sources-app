from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus

from middleware.decorators import api_key_required, permissions_required
from middleware.enums import PermissionsEnum


@pytest.fixture
def dummy_api_key_required_route():
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


def test_api_key_required(dummy_api_key_required_route, monkeypatch):
    mock_check_api_key = MagicMock()
    monkeypatch.setattr("middleware.decorators.check_api_key", mock_check_api_key)

    dummy_api_key_required_route()
    mock_check_api_key.assert_called_once()


@pytest.fixture
def dummy_permissions_required_route():
    @permissions_required(PermissionsEnum.READ_ALL_USER_INFO)
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route

def test_permissions_required(dummy_permissions_required_route, monkeypatch):
    mock_check_permissions = MagicMock()
    monkeypatch.setattr("middleware.decorators.check_permissions", mock_check_permissions)

    dummy_permissions_required_route()
    mock_check_permissions.assert_called_once_with(
        PermissionsEnum.READ_ALL_USER_INFO
    )