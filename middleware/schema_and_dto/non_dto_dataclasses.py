from dataclasses import dataclass
from typing import Callable, Any

from flask_restx import OrderedModel
from flask_restx.reqparse import RequestParser
from marshmallow import Schema
from pydantic import BaseModel

from utilities.enums import SourceMappingEnum


@dataclass
class FlaskRestxDocInfo:
    parser: RequestParser | None = None
    model: OrderedModel | None = None


@dataclass
class SchemaPopulateParameters:
    schema: type[Schema] | Schema
    dto_class: type[BaseModel]
    load_file: bool = False


class DTOPopulateParameters(BaseModel):
    """
    Parameters for the dynamic DTO population function
    """

    class Config:
        arbitrary_types_allowed = True

    dto_class: type[BaseModel] | type[Any]
    source: SourceMappingEnum | None = None
    transformation_functions: dict[str, Callable] | None = None
    attribute_source_mapping: dict[str, SourceMappingEnum] | None = None
    # A schema to be used for validating the input of the class.
    validation_schema: type[Schema] | Schema | None = None
