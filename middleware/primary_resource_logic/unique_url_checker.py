from flask import Response, make_response
from marshmallow import Schema, fields
from pydantic import BaseModel

from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from middleware.util.url import normalize_url
from utilities.enums import SourceMappingEnum


class UniqueURLCheckerRequestSchema(Schema):
    url = fields.Str(
        required=True,
        metadata={
            "description": "The URL to check.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "transformation_function": normalize_url,
        },
    )


class UniqueURLCheckerRequestDTO(BaseModel):
    url: str


class UniqueURLCheckerResponseInnerSchema(Schema):
    original_url = fields.Str(
        required=True,
        metadata={
            "description": "The URL of the duplicate.",
            "source": SourceMappingEnum.JSON,
        },
    )
    approval_status = fields.Enum(
        required=True,
        enum=ApprovalStatus,
        by_value=fields.Str,
        metadata={
            "description": "The approval status of the URL.",
            "source": SourceMappingEnum.JSON,
        },
    )
    rejection_note = fields.Str(
        required=False,
        metadata={
            "description": "The rejection note of the URL.",
            "source": SourceMappingEnum.JSON,
        },
    )


class UniqueURLCheckerResponseOuterSchema(Schema):
    duplicates = fields.List(
        fields.Nested(
            UniqueURLCheckerResponseInnerSchema,
            required=True,
            metadata={
                "description": "The list of duplicate URLs.",
                "source": SourceMappingEnum.JSON,
            },
        ),
        required=True,
        metadata={
            "description": "The list of duplicate URLs.",
            "source": SourceMappingEnum.JSON,
        },
    )


def unique_url_checker_wrapper(
    db_client: DatabaseClient, dto: UniqueURLCheckerRequestDTO
) -> Response:
    return make_response({"duplicates": db_client.check_for_url_duplicates(dto.url)})
