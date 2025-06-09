from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class GithubDataRequestsIssuesPostResponseSchema(Schema):
    message = fields.Str(
        required=True,
        metadata={
            "description": "The success message",
            "source": SourceMappingEnum.JSON,
        },
    )
    github_issue_url = fields.Str(
        required=True,
        metadata={
            "description": "The url of the created github issue",
            "source": SourceMappingEnum.JSON,
        },
    )
