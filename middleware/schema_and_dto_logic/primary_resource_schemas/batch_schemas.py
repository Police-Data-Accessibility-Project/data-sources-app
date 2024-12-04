from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


class BatchRequestSchema(Schema):

    file = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.FILE,
            "description": "The file to upload",
        },
    )


class BatchPostResponseSchema(MessageSchema):
    ids = fields.List(
        fields.Integer(metadata=get_json_metadata("The ids of the resources created")),
        required=True,
        metadata=get_json_metadata("The ids of the resources created"),
    )
    errors = fields.List(
        fields.String(
            metadata=get_json_metadata(
                "The errors associated with resources not created"
            )
        ),
        required=True,
        metadata=get_json_metadata("The errors associated with resources not created"),
    )


class BatchPutResponseSchema(MessageSchema):
    errors = fields.List(
        fields.String(
            metadata=get_json_metadata(
                "The errors associated with resources not updated"
            )
        ),
        required=True,
        metadata=get_json_metadata("The errors associated with resources not updated"),
    )
