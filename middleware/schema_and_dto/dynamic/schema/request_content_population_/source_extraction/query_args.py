from typing import final

from flask import request

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.validate import \
    validate_fields


@final
class QueryArgExtractor:

    def __init__(
        self,
        expected_fields: list[str],
    ):
        self.expected_fields = expected_fields
        self.query_args = request.args
        validate_fields(
            expected_fields=self.expected_fields,
            actual_fields=list(self.query_args.keys()),
        )

    def get(self, key: str) -> str:
        return self.query_args.get(key)
