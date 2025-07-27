from abc import ABC, abstractmethod

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.validate import \
    validate_fields
from middleware.schema_and_dto.dynamic.schema.request_content_population_.types import JSONDict


class SourceExtractorBase(ABC):

    def __init__(self, expected_fields: list[str]):
        self.expected_fields: list[str] = expected_fields
        self._data: dict[str, JSONDict] = self._extract()
        validate_fields(
            expected_fields=self.expected_fields,
            actual_fields=list(self._data.keys()),
        )

    @abstractmethod
    def _extract(self) -> dict[str, JSONDict]:
        raise NotImplementedError

    @property
    def data(self) -> dict[str, JSONDict]:
        return self._data
