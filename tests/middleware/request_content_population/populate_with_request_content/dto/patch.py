from unittest.mock import MagicMock


def patch_request_args_get(monkeypatch, path: str, request_args: dict) -> MagicMock:
    mock_request = MagicMock()
    monkeypatch.setattr(f"{path}.request", mock_request)
    mock_request.args.get = lambda arg: request_args.get(arg)
    mock_request.form.get = lambda arg: request_args.get(arg)
    mock_request.json.get = lambda arg: request_args.get(arg)
    return mock_request
