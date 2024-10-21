from typing import Any
from unittest.mock import MagicMock, patch

from tests.helper_scripts.constants import TEST_RESPONSE


def multi_monkeypatch(
    monkeypatch: patch, patch_root: str, mock: MagicMock, functions_to_patch: list[str]
) -> None:
    """
    Patches the given mock with all functions in the given list
    Each function will be accessible from the mock via an attribute with the same name as the funciton.
    :param monkeypatch:
    :param patch_root: The root of the patch, denoting the module where all functions are patched
    :param mock: The mock object which will be patched
    :param functions_to_patch: The functions to patch the mock object with
    :return:
    """
    for function_name in functions_to_patch:
        monkeypatch.setattr(
            target=f"{patch_root}.{function_name}", name=mock.__getattr__(function_name)
        )


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


def patch_request_args_get(monkeypatch, path: str, request_args: dict) -> MagicMock:
    mock_request = MagicMock()
    monkeypatch.setattr(f"{path}.request", mock_request)
    mock_request.args.get = lambda arg: request_args.get(arg)
    mock_request.form.get = lambda arg: request_args.get(arg)
    mock_request.json.get = lambda arg: request_args.get(arg)
    return mock_request


def patch_request_headers(monkeypatch, path: str, request_headers: dict) -> MagicMock:
    mock_request = MagicMock()
    monkeypatch.setattr(f"{path}.request", mock_request)
    mock_request.headers = request_headers
    return mock_request


def patch_abort(monkeypatch, path: str) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(f"{path}.abort", mock)
    return mock


def patch_and_return_mock(path: str, monkeypatch, returns_test_response: bool = False) -> MagicMock:
    mock = MagicMock()
    if returns_test_response:
        mock.return_value = TEST_RESPONSE
    monkeypatch.setattr(path, mock)
    return mock

def patch_make_response(path: str, monkeypatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(f"{path}.make_response", mock)
    return mock
