from typing import Optional
from unittest.mock import MagicMock

from utilities.DynamicRequestDTO import DynamicRequestDTO


class SampleDynamicRequestDTO(DynamicRequestDTO):
    simple_string: str
    optional_int: Optional[int] = None
    transformed_array: Optional[list[str]] = None

    def _transform_transformed_array(self, value: str) -> Optional[list[str]]:
        if value is None:
            return None
        return value.split(",")

SAMPLE_REQUEST_ARGS = {
    "simple_string": "spam",
    "optional_int": None,
    "transformed_array": "hello,world"
}

def test_sample_request(monkeypatch):
    mock_request = MagicMock()
    monkeypatch.setattr("utilities.DynamicRequestDTO.request", mock_request)
    mock_request.args.get = lambda arg: SAMPLE_REQUEST_ARGS[arg]
    dto = SampleDynamicRequestDTO()
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == ["hello", "world"]