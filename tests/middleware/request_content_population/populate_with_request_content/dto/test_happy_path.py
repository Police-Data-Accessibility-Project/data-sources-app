from typing import Optional

import pytest

from middleware.schema_and_dto.dynamic.dto_request_content_population import (
    populate_dto_with_request_content,
)
from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters
from tests.middleware.request_content_population.data import SimpleDTO
from utilities.enums import SourceMappingEnum


def transform_array(value: str) -> Optional[list[str]]:
    if value is None:
        return None
    return value.split(",")


@pytest.mark.parametrize(
    "source_mapping_enum",
    (
        SourceMappingEnum.QUERY_ARGS,
        SourceMappingEnum.JSON,
    ),
)
def test_populate_dto_with_request_content_happy_path(
    source_mapping_enum, patched_get_data_from_source
):
    dto = populate_dto_with_request_content(
        DTOPopulateParameters(
            dto_class=SimpleDTO,
            transformation_functions={"transformed_array": transform_array},
            source=source_mapping_enum,
        )
    )
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == ["hello", "world"]


