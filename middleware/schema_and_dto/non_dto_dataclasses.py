from typing import Type, Optional, Callable, Any

from flask_restx import OrderedModel
from flask_restx.reqparse import RequestParser
from marshmallow import Schema
from pydantic import BaseModel
from dataclasses import dataclass

from utilities.enums import SourceMappingEnum


@dataclass
class FlaskRestxDocInfo:
    parser: Optional[RequestParser]
    model: Optional[OrderedModel] = None


@dataclass
class SchemaPopulateParameters:
    schema: type[Schema] | Schema
    dto_class: Type[BaseModel]
    load_file: bool = False


class DTOPopulateParameters(BaseModel):
    """
    Parameters for the dynamic DTO population function
    """

    class Config:
        arbitrary_types_allowed = True

    dto_class: Type[BaseModel] | Type[Any]
    source: Optional[SourceMappingEnum] = None
    transformation_functions: Optional[dict[str, Callable]] = None
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None
    # A schema to be used for validating the input of the class.
    validation_schema: Optional[Type[Schema]] = None
