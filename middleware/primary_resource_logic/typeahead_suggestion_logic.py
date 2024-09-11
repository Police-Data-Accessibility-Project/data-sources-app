from typing import Callable, Type

from marshmallow import Schema, fields, validate

from database_client.database_client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    TypeaheadDTO,
    TypeaheadSchema,
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
        example="Pennsylvania",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The state of the suggestion",
        },
    )
    county = fields.String(
        required=True,
        example="Allegheny",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The county of the suggestion",
        },
        allow_none=True
    )
    locality = fields.String(
        required=True,
        example="Pittsburgh",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The locality of the suggestion",
        },
        allow_none=True
    )



class TypeaheadLocationsResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        example="Pittsburgh",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The display name of the suggestion",
        },
    )
    type = fields.String(
        required=True,
        example="Locality",
        validate=validate.OneOf(["State", "County", "Locality"]),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The type of suggestion.",
        },
    )


class TypeaheadAgenciesResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        example="Springfield Police Agency",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The display name of the suggestion",
        },
    )
    jurisdiction_type = fields.String(
        required=True,
        description=f"The jurisdiction type.",
        validate=validate.OneOf(JURISDICTION_TYPES),
        example="school",
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The type of suggestion.",
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
