from typing import final, override

from flask import request

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction._base import \
    SourceExtractorBase
from middleware.schema_and_dto.dynamic.schema.request_content_population_.types import JSONValue


@final
class JsonExtractor(SourceExtractorBase):

    @override
    def _extract(self) -> dict[str, JSONValue]:
        return request.get_json()  # pyright: ignore [reportAny]

