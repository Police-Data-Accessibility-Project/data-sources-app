from dataclasses import dataclass
import re

from flask import Response
from marshmallow import Schema, fields, validate
from pydantic import BaseModel

from database_client.database_client import DatabaseClient
from database_client.enums import ApprovalStatus
from middleware.flask_response_manager import FlaskResponseManager
from utilities.enums import SourceMappingEnum


def normalize_url(source_url: str) -> str:
    # Remove 'https://', 'http://' from the beginning
    url = re.sub(r"^(https://|http://)", "", source_url)
    # Remove "www." from the beginning
    url = re.sub(r"^www\.", "", url)
    # Remove trailing '/'
    url = url.rstrip("/")

    return url


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
    return FlaskResponseManager.make_response(
        data={"duplicates": db_client.check_for_url_duplicates(dto.url)}
    )
