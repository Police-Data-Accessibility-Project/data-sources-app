from unittest.mock import MagicMock

from tests.helper_scripts.common_test_data import TEST_RESPONSE


def patch_test_response_to_resource(monkeypatch, path) -> MagicMock:
    """
    Patch a test response to a response-returning function in the resource directory
    :param monkeypatch:
    :param path:
    :return:
    """
    mock_test_response_to_resource = MagicMock(return_value=TEST_RESPONSE)
    monkeypatch.setattr(f"resources.{path}", mock_test_response_to_resource)
    return mock_test_response_to_resource