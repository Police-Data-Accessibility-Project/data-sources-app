from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum
from dataclasses import dataclass

class GithubDataRequestsIssuesPostRequestSchema(Schema):
    data_request_id = fields.Str(
        required=True,
        metadata={
            "description": "The id of the data request",
            "source": SourceMappingEnum.PATH,
        }
    )

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

@dataclass
class GithubDataRequestsIssuesPostDTO:
    data_request_id: int