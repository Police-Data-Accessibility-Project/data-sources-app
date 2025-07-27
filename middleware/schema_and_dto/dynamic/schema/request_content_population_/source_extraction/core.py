from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.mapping import \
    EXTRACTOR_MAPPING
from middleware.schema_and_dto.dynamic.schema.request_content_population_.types import JSONDict
from utilities.enums import SourceMappingEnum


def get_data_from_source(source: SourceMappingEnum, fields: list[str]) -> JSONDict:
    extractor_class = EXTRACTOR_MAPPING[source]
    extractor = extractor_class(
        expected_fields=fields,
    )
    return extractor.data