from typing import final, override

from flask import request

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction._base import \
    SourceExtractorBase


@final
class QueryArgExtractor(SourceExtractorBase):

    @override
    def _extract(self) -> dict[str, str]:
        return request.args
