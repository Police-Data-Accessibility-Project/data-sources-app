# pyright: reportReturnType=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false
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

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Type

from flask_restx.reqparse import RequestParser

from flask_restx import fields as restx_fields, Namespace, OrderedModel
from marshmallow import fields as marshmallow_fields, missing, Schema
from marshmallow.fields import Field as MarshmallowField
from marshmallow.validate import OneOf

from middleware.schema_and_dto.mappings import (
    MARSHMALLOW_TO_RESTX_FIELD_MAPPING,
    RESTX_FIELD_TO_NATIVE_TYPE_MAPPING,
)
from middleware.schema_and_dto.non_dto_dataclasses import FlaskRestxDocInfo
from middleware.schema_and_dto.enums import RestxModelPlaceholder
from middleware.schema_and_dto.types import (
    MarshmallowFields,
    RestxFields,
    SchemaTypes,
)

from middleware.schema_and_dto.util import _get_required_argument
from endpoints._helpers.docs import create_variable_columns_model
from utilities.enums import SourceMappingEnum

PARSER_FIELDS = [
    SourceMappingEnum.QUERY_ARGS,
    SourceMappingEnum.PATH,
    SourceMappingEnum.FILE,
]

PARSER_SOURCE_LOCATION_MAP = {
    SourceMappingEnum.QUERY_ARGS: "query",
    SourceMappingEnum.PATH: "path",
    SourceMappingEnum.FILE: "file",
}


# region Supporting Functions
def get_location(source: SourceMappingEnum) -> str:
    return PARSER_SOURCE_LOCATION_MAP[source]


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


# endregion


# region Classes
def add_description_info_from_enum(
    field_value: marshmallow_fields.Enum, description: str
):
    enum_class = field_value.enum
    description += f" Must be one of: {[x.value for x in enum_class]}."
    return description


class DescriptionBuilder:
    """
    Appends information to description based on data
    in field
    """

    def __init__(self, field: marshmallow_fields, description: str):
        self.field = field
        self.description = description
        self.metadata = field.metadata

    def __str__(self):
        return self.description

    def build_description(self):
        self.enum_case()
        self.validator_case()
        self.list_query_case()
        self.default_case()

    def enum_case(self):
        if isinstance(self.field, marshmallow_fields.Enum):
            self.description = add_description_info_from_enum(
                field_value=self.field, description=self.description
            )

    def validator_case(self):
        for validator in self.field.validators:
            if isinstance(validator, OneOf):
                self.description = add_description_info_from_validators(
                    field=self.field, description=self.description
                )

    def list_query_case(self):
        if not isinstance(self.field, marshmallow_fields.List):
            return
        if not self.metadata.get("source") == SourceMappingEnum.QUERY_ARGS:
            return
        self.description += " \n(Comma-delimited list)"

    def default_case(self):
        default = self.field.load_default
        if default != missing:
            # If Enum, get value
            if isinstance(default, Enum):
                default = default.value
            self.description += f" \nDefault: {default}"


class FieldInfo:
    def __init__(
        self,
        field_name: str,
        field_value: marshmallow_fields.Field,
    ):
        self.field_name = field_name
        self.marshmallow_field_value = field_value
        self.marshmallow_field_type = type(field_value)
        self.parent_schema_instance = field_value.parent
        self.parent_schema_class = type(field_value.parent)
        self.metadata = field_value.metadata
        self.description = self._get_description(
            self.metadata,
            self.parent_schema_class,
            self.marshmallow_field_value,
            field_name,
        )
        self.required = field_value.required
        self.restx_field_type = self._map_field_type(self.marshmallow_field_type)
        self.source = _get_required_argument(
            "source", self.metadata, self.parent_schema_class
        )

    def _get_description(
        self,
        metadata: dict,
        schema_class: Type[SchemaTypes],
        field_value: MarshmallowField,
        field_name: str,
    ) -> str:
        description = _get_required_argument(
            "description", metadata, schema_class, field_name
        )
        desc_builder = DescriptionBuilder(field=field_value, description=description)
        desc_builder.build_description()
        return str(desc_builder)

    def _map_field_type(self, field_type: type[MarshmallowFields]) -> Type[RestxFields]:
        try:
            return MARSHMALLOW_TO_RESTX_FIELD_MAPPING[field_type]
        except KeyError:
            raise NotImplementedError(
                f"The marshmallow field type {field_type} is not currently supported for Restx field conversion"
            )

    def map_native_type(self, restx_field_type: Type[RestxFields]) -> type:
        try:
            return RESTX_FIELD_TO_NATIVE_TYPE_MAPPING[restx_field_type]
        except KeyError:
            raise NotImplementedError(
                f"The restx field type {restx_field_type} is not currently supported for mapping to a native python type"
            )

    def get_location(self, source: SourceMappingEnum) -> str:
        return get_location(source)


# region Restx Builders
class RestxBuilder(ABC):
    def add_fields(self, fields: list[FieldInfo]):
        for field in fields:
            self.add_field(field)

    @abstractmethod
    def add_field(self, fi: FieldInfo):
        raise NotImplementedError


class RestxParserBuilder(RestxBuilder):
    """
    Builds a Restx parser from Marshmallow fields
    """

    def __init__(self, parser: RequestParser):
        self.parser = parser

    def add_field(self, field_info: FieldInfo):
        fi = field_info
        self.parser.add_argument(
            fi.field_name,
            type=fi.map_native_type(fi.restx_field_type),
            required=fi.required,
            location=fi.get_location(fi.source),
            help=fi.description,
            default=fi.metadata.get("default"),
        )


class RestxModelBuilder(RestxBuilder):
    """
    Builds a Restx model from a marshmallow schema
    """

    def __init__(self, namespace: Namespace, model_name: Optional[str] = None):
        self.namespace = namespace
        self.model_name = model_name
        self.model_dict = {}

    def add_field(self, fi: FieldInfo):
        field = self._get_restx_field(fi)
        self.model_dict[fi.field_name] = field

    def _get_restx_field(self, fi: FieldInfo) -> RestxFields:
        if fi.restx_field_type in [e for e in RestxModelPlaceholder]:
            return self.build_restx_submodel(fi.restx_field_type, fi)
        if fi.restx_field_type == restx_fields.Nested:
            return self._build_nested_field_as_model(fi)
        if fi.restx_field_type == restx_fields.List:
            return self._build_list_field(fi)
        return fi.restx_field_type(required=fi.required, description=fi.description)

    def _build_list_field(self, fi: FieldInfo):
        # Get interior field of Marshmallow List
        inner_field = (
            fi.marshmallow_field_value.inner
        )  # pyright: ignore[reportAttributeAccessIssue]

        inner_field_info = FieldInfo(
            field_name=inner_field.name,
            field_value=inner_field,
        )
        inner_restx_field = self._get_restx_field(inner_field_info)

        return restx_fields.List(inner_restx_field, attribute=fi.field_name)

    def build_restx_submodel(self, placeholder: RestxModelPlaceholder, fi: FieldInfo):
        """
        Build a model that will be placed within the model
        :param placeholder:
        :param fi:
        :return:
        """

        if placeholder == RestxModelPlaceholder.VARIABLE_COLUMNS:
            return restx_fields.Nested(
                create_variable_columns_model(
                    namespace=self.namespace, name_snake_case=fi.field_name
                )
            )
        elif placeholder == RestxModelPlaceholder.LIST_VARIABLE_COLUMNS:
            return restx_fields.List(
                restx_fields.Nested(
                    create_variable_columns_model(
                        namespace=self.namespace, name_snake_case="result"
                    )
                ),
                attribute=fi.field_name,
            )

    def build_model(self) -> Optional[OrderedModel]:
        if self.model_dict == {}:
            return None
        return self.namespace.model(self.model_name, self.model_dict)

    def _build_nested_field_as_model(self, fi: FieldInfo):
        sub_schema = (
            fi.marshmallow_field_value.schema
        )  # pyright: ignore[reportAttributeAccessIssue]
        sorter = MarshmallowFieldSorter(sub_schema)
        self._raise_if_nonzero_parser_fields(fi, sorter)
        fields = MarshmallowFieldSorter(sub_schema).model_fields
        self._raise_if_no_model_fields(fi, fields)
        submodel_builder = RestxModelBuilder(
            namespace=self.namespace,
            model_name=f"{self.model_name} {fi.field_name}",
        )
        submodel_builder.add_fields(fields)
        submodel = submodel_builder.build_model()

        return restx_fields.Nested(
            submodel, required=fi.required, description=fi.description
        )

    def _raise_if_nonzero_parser_fields(self, fi, sorter):
        if len(sorter.parser_fields) != 0:
            parser_field_names = [x.field_name for x in sorter.parser_fields]
            raise ValueError(
                f"Nested Model `{fi.field_name}` in model `{self.model_name}` "
                f"has fields that are identified as parser fields."
                f"({parser_field_names})"
            )

    def _raise_if_no_model_fields(self, fi, fields):
        if len(fields) == 0:
            raise ValueError(f"Nested model {fi.field_name} has no fields")


# endregion


class MarshmallowFieldSorter:
    """
    Sorts Marshmallow fields into either a list of parser fields and a list of model fields
    """

    def __init__(self, schema: Schema | type[Schema]):
        self.parser_fields = []
        self.model_fields = []
        self.sort_fields(schema)

    def sort_fields(self, schema: Schema | type[Schema]):
        if hasattr(schema, "dump_fields"):
            fields = schema.dump_fields
        else:
            fields = schema._declared_fields
        for field_name, field_value in fields.items():
            fi = FieldInfo(
                field_name=field_name,
                field_value=field_value,
            )
            self._sort_field(fi)

    def _sort_field(self, fi: FieldInfo):
        if fi.source in PARSER_FIELDS:
            self.parser_fields.append(fi)
        elif fi.source == SourceMappingEnum.JSON:
            self.model_fields.append(fi)
        else:
            raise Exception(f"Source {fi.source} not supported")


class RestxParamDocumentationBuilder:
    def __init__(
        self,
        namespace: Namespace,
        schema: Schema | type[Schema],
        model_name: Optional[str] = None,
    ):
        model_name = model_name or schema.__class__.__name__
        self.parser_builder = RestxParserBuilder(namespace.parser())
        self.model_builder = RestxModelBuilder(
            namespace=namespace, model_name=model_name
        )
        self.namespace = namespace  #
        self.schema_class = schema

    def build(self) -> FlaskRestxDocInfo:
        self._populate_fields()
        return FlaskRestxDocInfo(
            model=self.model_builder.build_model(),
            parser=self.parser_builder.parser,
        )

    def _populate_fields(self):
        field_sorter = MarshmallowFieldSorter(self.schema_class)
        self.parser_builder.add_fields(field_sorter.parser_fields)
        self.model_builder.add_fields(field_sorter.model_fields)


def get_restx_param_documentation(
    namespace: Namespace,
    schema: type[Schema],
    model_name: Optional[str] = None,
) -> FlaskRestxDocInfo:
    """
    Takes a Marshmallow schema class with custom arguments and
    returns a Flask-RESTX model and Request Parser for Restx documentation, correlating to the schema
    Special arguments in schema fields include:
        * source: The source from which the arguments will be derived
        * default: The default value for the field
        * location: The location of url parameters (either "path" or "query")
    :param namespace:
    :param schema:
    :param model_name:
    :return:
    """
    builder = RestxParamDocumentationBuilder(namespace, schema, model_name)
    return builder.build()


# endregion
