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
        description="The state of the suggestion",
        example="Pennsylvania",
        metadata=RESPONSE_METADATA,
    )
    county = fields.String(
        required=True,
        description="The county of the suggestion",
        example="Allegheny",
        metadata=RESPONSE_METADATA,
    )
    locality = fields.String(
        required=True,
        description="The locality of the suggestion",
        example="Pittsburgh",
        metadata=RESPONSE_METADATA,
    )



class TypeaheadLocationsResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        description="The display name of the suggestion",
        example="Pittsburgh",
        metadata=RESPONSE_METADATA,
    )
    type = fields.String(
        required=True,
        description="The type of suggestion.",
        example="Locality",
        validate=validate.OneOf(["State", "County", "Locality"]),
        metadata=RESPONSE_METADATA,
    )


class TypeaheadAgenciesResponseSchema(TypeaheadBaseResponseSchema):
    display_name = fields.String(
        required=True,
        description="The display name of the suggestion",
        example="Springfield Police Agency",
        metadata=RESPONSE_METADATA,
    )
    jurisdiction_type = fields.String(
        required=True,
        description=f"The jurisdiction type.",
        validate=validate.OneOf(JURISDICTION_TYPES),
        example="school",
        metadata=RESPONSE_METADATA,
    )

# TODO: Use these in the integration tests
class TypeaheadAgenciesOuterResponseSchema(Schema):
    # pass
    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadAgenciesResponseSchema,
            required=True,
            description="The suggestions for the given query",
            metadata=RESPONSE_METADATA,
        ),
        metadata=RESPONSE_METADATA,
        description="The suggestions for the given query",
    )


class TypeaheadLocationsOuterResponseSchema(Schema):

    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadLocationsResponseSchema,
            required=True,
            description="The suggestions for the given query",
            metadata=RESPONSE_METADATA,
        ),
        metadata=RESPONSE_METADATA,
        description="The suggestions for the given query",
    )


def get_typeahead_results(
    db_client: DatabaseClient,
    dto: TypeaheadDTO,
    db_client_method: Callable,
):
    return FlaskResponseManager.make_response(
        data={"suggestions": db_client_method(db_client, dto.query)},
    )
