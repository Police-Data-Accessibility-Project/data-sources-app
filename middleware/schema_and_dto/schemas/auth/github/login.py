from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class GithubRequestSchema(Schema):
    gh_access_token = fields.Str(
        metadata=get_json_metadata("The access token for the user's Github account"),
    )
