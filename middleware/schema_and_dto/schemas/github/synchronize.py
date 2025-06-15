from marshmallow import Schema, fields

from middleware.schema_and_dto.schemas.github.issue import (
    GithubIssueURLInfosSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class GithubSynchronizeResponseSchema(Schema):
    message = fields.Str(
        require=True,
        metadata=get_json_metadata(
            description="The result of the synchronization request."
        ),
    )
    issues_created = fields.List(
        fields.Nested(
            nested=GithubIssueURLInfosSchema(),
            metadata=get_json_metadata(
                description="The urls of the created github issues."
            ),
        ),
        required=False,
        metadata=get_json_metadata(
            description="The urls of the created github issues."
        ),
    )
