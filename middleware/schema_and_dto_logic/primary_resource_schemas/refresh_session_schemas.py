from dataclasses import dataclass

from marshmallow import fields, Schema

from middleware.schema_and_dto_logic.util import get_json_metadata


class RefreshSessionRequestSchema(Schema):
    refresh_token = fields.String(
        required=True,
        metadata=get_json_metadata("The refresh token for the user's PDAP account"),
    )


@dataclass
class RefreshSessionRequestDTO:
    refresh_token: str
