from marshmallow import fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.schemas.agencies.get.base import AgenciesGetSchema
from utilities.enums import SourceMappingEnum


class AgenciesGetByIDResponseSchema(MessageSchema):
    data = fields.Nested(
        nested=AgenciesGetSchema(),
        required=True,
        metadata={
            "description": "The result",
            "source": SourceMappingEnum.JSON,
        },
    )
