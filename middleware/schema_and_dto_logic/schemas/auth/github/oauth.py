from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_query_metadata


class GithubOAuthRequestSchema(Schema):
    redirect_url = fields.Str(
        required=False,
        metadata=get_query_metadata(
            "The URL to redirect the user to after authorization. "
            "After authorization, the user will be redirected to this URL with a query parameter"
            " containing the access token."
        ),
    )
