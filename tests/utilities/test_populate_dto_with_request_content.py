from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock

import flask_restx
import pytest
from flask_restx import Namespace, Model
from flask_restx.reqparse import RequestParser
from marshmallow import Schema, fields, validate, ValidationError

from tests.helper_scripts.common_mocks_and_patches import patch_request_args_get
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
    InvalidSourceMappingError,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_dto_request_content_population import (
    populate_dto_with_request_content,
    _optionally_check_against_schema,
)
from middleware.schema_and_dto_logic.custom_exceptions import AttributeNotInClassError
from utilities.enums import SourceMappingEnum
from utilities.argument_checking_logic import (
    MutuallyExclusiveArgumentError,
    MissingRequiredArgumentError,
)


@dataclass
class SimpleDTO:
    simple_string: str
    optional_int: Optional[int] = None
    transformed_array: Optional[list[str]] = None


def transform_array(value: str) -> Optional[list[str]]:
    if value is None:
        return None
    return value.split(",")


SAMPLE_REQUEST_ARGS = {
    "simple_string": "spam",
    "optional_int": None,
    "transformed_array": "hello,world",
}

ROUTE_TO_PATCH = "middleware.schema_and_dto_logic.util"


@pytest.fixture
def patched_request_args_get(monkeypatch):
    return patch_request_args_get(monkeypatch, ROUTE_TO_PATCH, SAMPLE_REQUEST_ARGS)


@pytest.mark.parametrize(
    "source_mapping_enum",
    (
        SourceMappingEnum.QUERY_ARGS,
        SourceMappingEnum.FORM,
        SourceMappingEnum.JSON,
    ),
)
def test_populate_dto_with_request_content_happy_path(
    source_mapping_enum, patched_request_args_get
):

    dto = populate_dto_with_request_content(
        SimpleDTO,
        transformation_functions={"transformed_array": transform_array},
        source=source_mapping_enum,
    )
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == ["hello", "world"]


def test_populate_dto_with_request_transformation_function_not_in_attributes(
    patched_request_args_get,
):
    """
    Test that an error is raised if the attribute provided in the transformation function is not in the attributes
    :return:
    """
    with pytest.raises(AttributeNotInClassError):
        dto = populate_dto_with_request_content(
            SimpleDTO,
            transformation_functions={"non_existent_attribute": lambda value: value},
            source=SourceMappingEnum.QUERY_ARGS,
        )


def test_populate_dto_with_request_no_transformation_functions(
    patched_request_args_get,
):
    dto = populate_dto_with_request_content(
        SimpleDTO,
        source=SourceMappingEnum.QUERY_ARGS,
    )
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == "hello,world"


def test_populate_dto_with_request_source_mapping_and_source_arguments(
    patched_request_args_get,
):
    with pytest.raises(MutuallyExclusiveArgumentError):
        dto = populate_dto_with_request_content(
            SimpleDTO,
            source=SourceMappingEnum.QUERY_ARGS,
            attribute_source_mapping={"simple_string": SourceMappingEnum.FORM},
        )


def test_populate_dto_with_request_no_source_argument(
    patched_request_args_get,
):
    with pytest.raises(MissingRequiredArgumentError):
        dto = populate_dto_with_request_content(SimpleDTO)


def test_populate_dto_with_request_source_mapping_happy_path(
    patched_request_args_get,
):
    mock_request = patched_request_args_get
    mock_request.args.get = MagicMock(return_value=1)
    mock_request.form.get = MagicMock(return_value=2)
    mock_request.json.get = MagicMock(return_value=3)
    dto = populate_dto_with_request_content(
        SimpleDTO,
        attribute_source_mapping={
            "simple_string": SourceMappingEnum.QUERY_ARGS,
            "optional_int": SourceMappingEnum.FORM,
            "transformed_array": SourceMappingEnum.JSON,
        },
    )
    mock_request.json.get.assert_called_once_with("transformed_array")
    mock_request.form.get.assert_called_once_with("optional_int")
    mock_request.args.get.assert_called_once_with("simple_string")

    assert dto.simple_string == 1
    assert dto.optional_int == 2
    assert dto.transformed_array == 3


class ExampleSchema(Schema):
    example_string = fields.String(
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example string",
    )
    example_query_string = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string",
    )
    example_form = fields.String(
        required=True,
        source=SourceMappingEnum.FORM,
        description="An example form string",
    )


class ExampleSchemaWithoutForm(Schema):
    example_string = fields.String(
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example string",
    )
    example_query_string = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string",
    )


@dataclass
class ExampleDTO:
    example_string: str
    example_query_string: str
    example_form: str


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


class ExampleSchemaWithEnum(Schema):
    example_enum = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string.",
        validate=validate.OneOf(["a", "b"]),
    )


@dataclass
class ExampleDTOWithEnum:
    example_enum: str


def test_populate_schema_with_request_content(
    patched_request_args_get,
):
    mock_request = patched_request_args_get
    mock_request.json.get = MagicMock(return_value="json value")
    mock_request.args.get = MagicMock(return_value="arg value")
    mock_request.form.get = MagicMock(return_value="form value")

    obj = populate_schema_with_request_content(
        schema=ExampleSchema(), dto_class=ExampleDTO
    )

    assert isinstance(obj, ExampleDTO)
    assert obj.example_string == "json value"
    assert obj.example_query_string == "arg value"
    assert obj.example_form == "form value"


class ExampleNestedSchema(Schema):
    example_dto_with_enum = fields.Nested(
        ExampleSchemaWithEnum,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example description.",
        metadata={
            "nested_dto_class": ExampleDTOWithEnum,
        },
    )
    example_dto = fields.Nested(
        ExampleSchema,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example description.",
        metadata={"nested_dto_class": ExampleDTO},
    )


@dataclass
class ExampleNestedDTO:
    example_dto_with_enum: ExampleDTOWithEnum
    example_dto: ExampleDTO


class ExampleNestedSchemaWithIncorrectSource(Schema):
    example_dto_with_enum = fields.Nested(
        ExampleSchemaWithEnum,
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string.",
    )
    example_dto = fields.Nested(
        ExampleSchema,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example query string.",
    )


def test_populate_nested_schema_with_request_content_non_json_source_provided(
    patched_request_args_get,
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


def test_populate_nested_schema_with_request_content(
    monkeypatch,
):
    mock = patch_request_args_get(
        monkeypatch,
        ROUTE_TO_PATCH,
        {
            "example_dto_with_enum": {"example_enum": "a"},
            "example_dto": {
                "example_string": "my example string",
                "example_query_string": "my example query string",
                "example_form": "form value",
            },
        },
    )

    obj = populate_schema_with_request_content(
        schema=ExampleNestedSchema(), dto_class=ExampleNestedDTO
    )

    assert isinstance(obj, ExampleNestedDTO)
    assert obj.example_dto_with_enum.example_enum == "a"
    assert obj.example_dto.example_string == "my example string"
    assert obj.example_dto.example_query_string == "my example query string"
    assert obj.example_dto.example_form == "form value"


def test_get_restx_param_documentation():

    result = get_restx_param_documentation(
        namespace=Namespace(name="test", path="/test", description="test"),
        schema=ExampleSchemaWithoutForm,
        model_name="ExampleDTOWithoutForm",
    )

    assert isinstance(result.model, Model)
    assert result.model.name == "ExampleDTOWithoutForm"
    assert result.model["example_string"].description == "An example string"
    assert isinstance(result.model["example_string"], flask_restx.fields.String)
    assert isinstance(result.parser, RequestParser)
    assert result.parser.args[0].help == "An example query string"
    assert isinstance(result.parser.args[0], flask_restx.reqparse.Argument)
    assert result.parser.args[0].required is True


def test_get_restx_param_documentation_with_enum():
    """
    Test that description properly appended to description of enum field (i.e. a field with limited values)
    """

    result = get_restx_param_documentation(
        namespace=Namespace(name="test", path="/test", description="test"),
        schema=ExampleSchemaWithEnum,
        model_name="ExampleDTOWithEnum",
    )

    assert (
        result.parser.args[0].help
        == "An example query string. Must be one of: ['a', 'b']."
    )
