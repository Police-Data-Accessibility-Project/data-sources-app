from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction._base import (
    SourceExtractorBase,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.impl.json_ import (
    JsonExtractor,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.impl.path import (
    PathExtractor,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.impl.query_args import (
    QueryArgExtractor,
)
from utilities.enums import SourceMappingEnum

EXTRACTOR_MAPPING: dict[SourceMappingEnum, type[SourceExtractorBase]] = {
    SourceMappingEnum.JSON: JsonExtractor,
    SourceMappingEnum.QUERY_ARGS: QueryArgExtractor,
    SourceMappingEnum.PATH: PathExtractor,
}
