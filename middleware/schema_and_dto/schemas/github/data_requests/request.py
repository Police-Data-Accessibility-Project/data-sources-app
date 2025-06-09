from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class GithubDataRequestsIssuesPostRequestSchema(Schema):
    data_request_id = fields.Str(
        required=True,
        metadata={
            "description": "The id of the data request",
            "source": SourceMappingEnum.PATH,
        },
    )
