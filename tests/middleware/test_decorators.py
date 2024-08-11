from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus

from middleware.decorators import api_key_required
from middleware.enums import PermissionsEnum


@pytest.fixture
def dummy_api_key_required_route_no_permission():
    @api_key_required()
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


@pytest.fixture
def dummy_api_key_required_route_with_permission():
    @api_key_required(PermissionsEnum.READ_ALL_USER_INFO)
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route

def test_api_key_required_no_permission(dummy_api_key_required_route_no_permission, monkeypatch):
    mock_check_api_key = MagicMock()
    monkeypatch.setattr("middleware.decorators.check_api_key", mock_check_api_key)

    dummy_api_key_required_route_no_permission()
    mock_check_api_key.assert_called_with(None)

def test_api_key_required_with_permission(dummy_api_key_required_route_with_permission, monkeypatch):
    mock_check_api_key = MagicMock()
    monkeypatch.setattr("middleware.decorators.check_api_key", mock_check_api_key)

    dummy_api_key_required_route_with_permission()
    mock_check_api_key.assert_called_with(PermissionsEnum.READ_ALL_USER_INFO)