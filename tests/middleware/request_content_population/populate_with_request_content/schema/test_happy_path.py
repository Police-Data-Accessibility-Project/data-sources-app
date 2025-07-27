from middleware.schema_and_dto.dynamic.schema.request_content_population_.core import \
    populate_schema_with_request_content
from tests.middleware.request_content_population.data import ExampleNestedSchema, ExampleNestedDTO


def test_populate_nested_schema_with_request_content(
    patched_get_source_data_info_from_sources,
):

    obj = populate_schema_with_request_content(
        schema=ExampleNestedSchema(), dto_class=ExampleNestedDTO
    )

    assert isinstance(obj, ExampleNestedDTO)
    assert obj.example_dto_with_enum.example_enum == "a"
    assert obj.example_dto.example_string == "my example string"
    assert obj.example_dto.example_query_string == "my example query string"
