from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class ResetPasswordRequestSchema(Schema):
    email = fields.Str(
        required=True,
        metadata={
            "description": "The email of the user",
            "source": SourceMappingEnum.JSON,
        },
    )
    token = fields.Str(
        required=True,
        metadata={
            "description": "The token of the user",
            "source": SourceMappingEnum.JSON,
        },
    )


class ResetPasswordSchema(Schema):
    password = fields.Str(
        required=True,
        metadata={
            "description": "The new password of the user",
            "source": SourceMappingEnum.JSON,
        },
    )
