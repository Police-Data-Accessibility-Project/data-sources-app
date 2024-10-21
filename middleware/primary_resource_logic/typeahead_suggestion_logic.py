from typing import Callable, Type

from marshmallow import Schema, fields, validate

from database_client.database_client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    TypeaheadDTO,
    TypeaheadQuerySchema,
)
from utilities.enums import SourceMappingEnum

JURISDICTION_TYPES = [
    "school",
    None,
    "county",
    "local",
    "port",
    "tribal",
    "transit",
    "state",
    "federal",
]


RESPONSE_METADATA = {
    "source": SourceMappingEnum.JSON,
}


class TypeaheadBaseResponseSchema(Schema):
    state = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The state of the suggestion",
            "example": "Pennsylvania",
        },
    )
    county = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The county of the suggestion",
            "example": "Allegheny",
        },
        allow_none=True,
    )
    locality = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The locality of the suggestion",
            "example": "Pittsburgh",
        },
        allow_none=True,
    )


class TypeaheadLocationsResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The display name of the suggestion",
            "example": "Pittsburgh",
        },
    )
    type = fields.String(
        required=True,
        validate=validate.OneOf(["State", "County", "Locality"]),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The type of suggestion.",
            "example": "Locality",
        },
    )


class TypeaheadAgenciesResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The display name of the suggestion",
            "example": "Springfield County Sheriff's Office",
        },
    )
    jurisdiction_type = fields.String(
        required=True,
        validate=validate.OneOf(JURISDICTION_TYPES),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The jurisdiction type.",
            "example": "school",
        },
    )


# TODO: Use these in the integration tests
class TypeaheadAgenciesOuterResponseSchema(Schema):
    # pass
    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadAgenciesResponseSchema,
            required=True,
            metadata={
                "source": SourceMappingEnum.JSON,
                "description": "The suggestions for the given query",
            },
        ),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The suggestions for the given query",
        },
    )


class TypeaheadLocationsOuterResponseSchema(Schema):

    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadLocationsResponseSchema,
            required=True,
            metadata={
                "source": SourceMappingEnum.JSON,
                "description": "The suggestions for the given query",
            },
        ),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The suggestions for the given query",
        },
    )


def get_typeahead_results(
    db_client: DatabaseClient,
    dto: TypeaheadDTO,
    db_client_method: Callable,
):
    return FlaskResponseManager.make_response(
        data={"suggestions": db_client_method(db_client, dto.query)},
    )
