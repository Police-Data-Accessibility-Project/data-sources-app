from marshmallow import fields

from middleware.schema_and_dto.schemas.auth.github.login import (
    GithubRequestSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class LinkToGithubRequestSchema(GithubRequestSchema):
    user_email = fields.Str(
        metadata=get_json_metadata("The email address of the user"),
    )
