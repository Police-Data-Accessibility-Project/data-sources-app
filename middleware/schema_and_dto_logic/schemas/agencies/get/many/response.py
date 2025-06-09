from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.common.common_response_schemas import (
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.schemas.agencies.get.base import AgenciesGetSchema
from utilities.enums import SourceMappingEnum


class AgenciesGetManyResponseSchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=AgenciesGetSchema(),
            required=True,
            metadata={
                "description": "The list of results",
                "source": SourceMappingEnum.JSON,
            },
        ),
        required=True,
        metadata={
            "description": "The list of results",
            "source": SourceMappingEnum.JSON,
        },
    )
