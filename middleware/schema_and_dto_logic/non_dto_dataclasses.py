from dataclasses import dataclass
from typing import Type, Optional

from flask_restx import Model
from flask_restx.reqparse import RequestParser

from middleware.schema_and_dto_logic.custom_types import SchemaTypes, DTOTypes


@dataclass
class FlaskRestxDocInfo:
    parser: RequestParser
    model: Optional[Model] = None


@dataclass
class SchemaPopulateParameters:
    schema_class: Type[SchemaTypes]
    dto_class: Type[DTOTypes]
