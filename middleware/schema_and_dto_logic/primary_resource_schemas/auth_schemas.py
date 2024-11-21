from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.util import get_json_metadata, get_query_metadata


class LoginResponseSchema(MessageSchema):
    access_token = fields.Str(
        metadata=get_json_metadata("The access token for the user's PDAP account"),
    )
    refresh_token = fields.Str(
        metadata=get_json_metadata("The refresh token for the user's PDAP account"),
    )


class GithubRequestSchema(Schema):
    gh_access_token = fields.Str(
        metadata=get_json_metadata("The access token for the user's Github account"),
    )


@dataclass
class LoginWithGithubRequestDTO:
    gh_access_token: str


class LinkToGithubRequestSchema(GithubRequestSchema):
    user_email = fields.Str(
        metadata=get_json_metadata("The email address of the user"),
    )


class GithubOAuthRequestSchema(Schema):
    redirect_url = fields.Str(
        required=False,
        metadata=get_query_metadata(
            "The URL to redirect the user to after authorization. "
            "After authorization, the user will be redirected to this URL with a query parameter"
            " containing the access token."
        ),
    )


@dataclass
class GithubOAuthRequestDTO:
    redirect_url: Optional[str] = None
