"""
This module aims to reduce the amount of boilerplate code
with retrieving requests and populating Data Transfer Objects (DTO)s
By dynamically populating an DTO with data from the request,
    based on the attributes defined in the DTO

# Schema Dynamic Population
In this module, we use the `marshmallow` library to dynamically
populate a data transfer object (DTO) with data from the request, as well as documentation
for the flask_restx namespace

A schema is defined with custom arguments for each field in the DTO.
These values are then populated with data from the request, in some cases with
transformation functions applied to convert them from a request-friendly format
into the native format of the DTO.

Note that this can sometimes lead to oddities such as a field being defined as a string
in the schema but as a list in the DTO.
This is because the request-friendly format is a string of comma-delimited values,
and the native format is a list, which the request-friendly format is converted to.
"""

from typing import Optional, Type

from flask_restx.reqparse import RequestParser

from flask_restx import fields as restx_fields, Namespace
from marshmallow import fields as marshmallow_fields
from marshmallow.validate import OneOf

from middleware.schema_and_dto_logic.mappings import MARSHMALLOW_TO_RESTX_FIELD_MAPPING, \
    RESTX_FIELD_TO_NATIVE_TYPE_MAPPING
from middleware.schema_and_dto_logic.non_dto_dataclasses import FlaskRestxDocInfo
from middleware.schema_and_dto_logic.enums import RestxModelPlaceholder
from middleware.schema_and_dto_logic.custom_types import MarshmallowFields, RestxFields, SchemaTypes
from middleware.schema_and_dto_logic.restx_param_intermediate_objects import RestxParamIntermediateObjects
from middleware.schema_and_dto_logic.util import _get_required_argument
from resources.resource_helpers import create_variable_columns_model
from utilities.enums import SourceMappingEnum


def get_location(source: SourceMappingEnum) -> str:
    if source == SourceMappingEnum.PATH:
        return "path"
    if source == SourceMappingEnum.QUERY_ARGS:
        return "query"


def add_description_info_from_validators(
    field: marshmallow_fields.Field, description: str
):
    """
    For some validators, add to the description information based on what the validator does
    :param field:
    :param description:
    :return:
    """
    for validator in field.validators:
        if isinstance(validator, OneOf):
            description += f" Must be one of: {validator.choices}."
    return description


class RestxFieldBuilder:
    """
    Builds a Restx field from a marshmallow field
    """

    def __init__(
        self,
        field_name: str,
        field_value: marshmallow_fields.Field,
        schema_class: Type[SchemaTypes],
        namespace: Namespace
    ):
        self.namespace = namespace
        self.field_name = field_name
        self.field_value = field_value
        self.schema_class = schema_class
        self.metadata = field_value.metadata
        self.description = self._get_description()
        self.required = field_value.required
        self.restx_field_type = self._map_field_type(type(field_value))
        self.source = _get_required_argument("source", self.metadata, self.schema_class)

    def _get_description(self) -> str:
        description = _get_required_argument(
            "description", self.metadata, self.schema_class
        )
        return add_description_info_from_validators(self.field_value, description)

    def _map_field_type(self, field_type: type[MarshmallowFields]) -> Type[RestxFields]:
        try:
            return MARSHMALLOW_TO_RESTX_FIELD_MAPPING[field_type]
        except KeyError:
            raise NotImplementedError(f"The marshmallow field type {field_type} is not currently supported for Restx field conversion")

    def _map_native_type(self, restx_field_type: Type[RestxFields]) -> type:
        try:
            return RESTX_FIELD_TO_NATIVE_TYPE_MAPPING[restx_field_type]
        except KeyError:
            raise NotImplementedError(f"The restx field type {restx_field_type} is not currently supported for mapping to a native python type")

    def build_restx_field(self, intermediate_object: RestxParamIntermediateObjects):
        if self.source == SourceMappingEnum.JSON:
            return self._build_json_field_as_model(intermediate_object.restx_model_dict)
        elif self.source in (SourceMappingEnum.QUERY_ARGS, SourceMappingEnum.PATH):
            return self._build_query_or_path_field(intermediate_object.parser)
        else:
            raise Exception(f"Source {self.source.value} not supported")

    def build_restx_model(
            self,
            placeholder: RestxModelPlaceholder,
            restx_model_dict: dict
    ):
        if placeholder == RestxModelPlaceholder.VARIABLE_COLUMNS:
            restx_model_dict[self.field_name] = restx_fields.Nested(create_variable_columns_model(
                namespace=self.namespace,
                name_snake_case=self.field_name
            ))
        elif placeholder == RestxModelPlaceholder.LIST_VARIABLE_COLUMNS:
            restx_model_dict[self.field_name] = restx_fields.List(
                restx_fields.Nested(
                    create_variable_columns_model(
                        namespace=self.namespace,
                        name_snake_case="result"
                    )
                ),
                attribute=self.field_name
            )


    def _build_json_field_as_model(
        self, restx_model_dict: dict
    ):
        if self.restx_field_type in [e for e in RestxModelPlaceholder]:
            self.build_restx_model(
                self.restx_field_type,
                restx_model_dict
            )
        else:
            restx_model_dict[self.field_name] = self.restx_field_type(
                required=self.required, description=self.description
            )

    def _build_query_or_path_field(
        self, parser: RequestParser
    ):
        parser.add_argument(
            self.field_name,
            type=self._map_native_type(self.restx_field_type),
            required=self.required,
            location=self._get_location(self.source),
            help=self.description,
            default=self.metadata.get("default"),
        )

    def _get_location(self, source: SourceMappingEnum) -> str:
        return get_location(source)


class RestxParamDocumentationBuilder:
    def __init__(
        self,
        namespace: Namespace,
        schema_class: Type[SchemaTypes],
        model_name: Optional[str] = None,
    ):
        model_name = model_name or schema_class.__name__  #
        self.intermediate_object = RestxParamIntermediateObjects(namespace, model_name)
        self.namespace = namespace  #
        self.schema_class = schema_class
        self.restx_model_dict = {}  #
        self.parser = self.namespace.parser()  #

    def build(self) -> FlaskRestxDocInfo:
        self._populate_fields()
        return self.intermediate_object.construct_doc_info()

    def _populate_fields(self):
        fields = self.schema_class().fields
        for field_name, field_value in fields.items():
            self._process_field(field_name, field_value)

    def _process_field(self, field_name: str, field_value: marshmallow_fields.Field):
        field_builder = RestxFieldBuilder(field_name, field_value, self.schema_class, self.namespace)
        field_builder.build_restx_field(self.intermediate_object)


def get_restx_param_documentation(
    namespace: Namespace, schema_class: Type[SchemaTypes], model_name: Optional[str] = None
):
    """
    Takes a Marshmallow schema class with custom arguments and
    returns a Flask-RESTX model and Request Parser for Restx documentation, correlating to the schema
    Special arguments in schema fields include:
        * source: The source from which the arguments will be derived
        * default: The default value for the field
        * location: The location of url parameters (either "path" or "query")
    :param namespace:
    :param schema_class:
    :param model_name:
    :return:
    """
    builder = RestxParamDocumentationBuilder(namespace, schema_class, model_name)
    return builder.build()


