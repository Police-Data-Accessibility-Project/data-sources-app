from typing import final

from flask import request

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.validate import \
    validate_fields
from middleware.schema_and_dto.dynamic.schema.request_content_population_.types import JSONValue


@final
class JsonExtractor:

    def __init__(self, expected_fields: list[str]):
        self.expected_fields = expected_fields
        self.json_data = request.get_json()
        validate_fields(
            expected_fields=self.expected_fields,
            actual_fields=list(self.json_data.keys()),
        )

    def get(self, key: str) -> JSONValue:
        return self.json_data[key]