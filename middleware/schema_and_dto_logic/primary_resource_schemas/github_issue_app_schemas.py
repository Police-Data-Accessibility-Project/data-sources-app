from marshmallow import Schema, fields
from pydantic import BaseModel

from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum
from dataclasses import dataclass


class GithubDataRequestsIssuesPostRequestSchema(Schema):
    data_request_id = fields.Str(
        required=True,
        metadata={
            "description": "The id of the data request",
            "source": SourceMappingEnum.PATH,
        },
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


class GithubDataRequestsIssuesPostDTO(BaseModel):
    data_request_id: int


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


class GithubIssueURLInfosDTO(BaseModel):
    github_issue_url: str
    data_request_id: int
