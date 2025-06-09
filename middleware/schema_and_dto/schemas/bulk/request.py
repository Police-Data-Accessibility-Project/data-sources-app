from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class BatchRequestSchema(Schema):

    file = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.FILE,
            "description": "The file to upload",
        },
    )
