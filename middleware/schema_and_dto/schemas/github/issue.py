from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class GithubIssueURLInfosSchema(Schema):
    github_issue_url = fields.Str(
        required=True,
        metadata={
            "description": "The url of the created github issue",
            "source": SourceMappingEnum.JSON,
        },
    )
    data_request_id = fields.Int(
        required=True,
        metadata={
            "description": "The id of the data request",
            "source": SourceMappingEnum.JSON,
        },
    )
