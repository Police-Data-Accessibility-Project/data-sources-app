import flask_restx
from flask_restx import Namespace, Model
from flask_restx.reqparse import RequestParser

from middleware.schema_and_dto.dynamic.schema.doc_construction.documentation_construction import \
    get_restx_param_documentation
from tests.middleware.request_content_population.data import ExampleSchemaWithoutForm, ExampleSchemaWithEnum


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
