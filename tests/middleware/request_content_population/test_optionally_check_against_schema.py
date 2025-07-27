import pytest
from marshmallow import ValidationError

from middleware.schema_and_dto.dynamic.dto_request_content_population import _optionally_check_against_schema
from tests.middleware.request_content_population.data import ExampleSchemaWithoutForm, ExampleSchema


def test_optionally_check_against_schema_none():
    example_values = {"hello": "world"}
    _optionally_check_against_schema(None, example_values)


def test_optionally_check_against_schema_valid_schema():
    example_values = {
        "example_string": "hello world",
        "example_query_string": "world hello",
    }
    _optionally_check_against_schema(ExampleSchemaWithoutForm, example_values)


def test_optionally_check_against_schema_invalid_schema():
    with pytest.raises(ValidationError):
        _optionally_check_against_schema(ExampleSchema, {"invalid_arg": 1})
