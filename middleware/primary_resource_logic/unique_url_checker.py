from dataclasses import dataclass
import re
from marshmallow import Schema, fields, validate

from database_client.enums import ApprovalStatus
from utilities.enums import SourceMappingEnum


def normalize_url(source_url: str) -> str:
    # Remove 'https://', 'http://', and 'www.' from the beginning
    url = re.sub(r"^(https://|http://|www\.)", "", source_url)
    # Remove trailing '/'
    url = url.rstrip("/")

    return url


class UniqueURLCheckerRequestSchema(Schema):
    url = fields.URL(
        required=True,
        metadata={
            "description": "The URL to check.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "transformation_function": normalize_url,
        },
    )


@dataclass
class UniqueURLCheckerRequestDTO:
    url: str


class UniqueURLCheckerResponseInnerSchema(Schema):
    url = fields.Str(
        required=True,
        metadata={
            "description": "The URL of the duplicate.",
            "source": SourceMappingEnum.JSON,
        },
    )
    approval_status = fields.Str(
        required=True,
        metadata={
            "description": "The approval status of the URL.",
            "source": SourceMappingEnum.JSON,
        },
        validate=validate.OneOf([e.value for e in ApprovalStatus]),
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

