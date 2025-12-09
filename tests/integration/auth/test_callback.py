from unittest.mock import MagicMock

from endpoints.instantiations.auth_.callback import Callback
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_callback(monkeypatch, test_data_creator_flask: TestDataCreatorFlask):
    # Mock run endpoint
    mock_run_endpoint = MagicMock(return_value={})
    monkeypatch.setattr(Callback, "run_endpoint", mock_run_endpoint)

    # Call endpoint
    test_data_creator_flask.request_validator.get(endpoint="/auth/callback")

    # Assert
    mock_run_endpoint.assert_called_once()
