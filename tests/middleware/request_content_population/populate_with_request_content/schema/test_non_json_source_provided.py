import pytest

from middleware.schema_and_dto.dynamic.schema.request_content_population_.core import \
    populate_schema_with_request_content
from middleware.schema_and_dto.dynamic.schema.request_content_population_.exceptions import InvalidSourceMappingError
from tests.middleware.request_content_population.data import ExampleNestedSchemaWithIncorrectSource, ExampleNestedDTO


def test_populate_nested_schema_with_request_content_non_json_source_provided(
    patched_get_source_data_info_from_sources,
):
    """
    If a schema is nested and the source is not JSON, an error should be raised
    :param patched_request_args_get:
    :return:
    """
    with pytest.raises(InvalidSourceMappingError):
        populate_schema_with_request_content(
            schema=ExampleNestedSchemaWithIncorrectSource(),
            dto_class=ExampleNestedDTO,
        )


