from marshmallow import Schema, fields

from endpoints.instantiations.search._shared.dtos.follow import FollowSearchResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from middleware.schema_and_dto.util import get_json_metadata


class FollowSearchResponseSchema(Schema):
    state_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The state of the search."),
    )
    display_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The display name of the search."),
    )
    county_name = fields.Str(
        required=False,
        allow_none=True,
        metadata=get_json_metadata(
            "The county of the search. If empty, all counties for the given state will be searched."
        ),
    )
    locality_name = fields.Str(
        required=False,
        allow_none=True,
        metadata=get_json_metadata(
            "The locality of the search. If empty, all localities for the given county will be searched."
        ),
    )
    location_id = fields.Int(
        required=True,
        metadata=get_json_metadata("The location ID of the search."),
    )
    subscriptions_by_category = fields.Dict(
        required=True,
        metadata=get_json_metadata("The record categories of the search."),
    )

FollowSearchResponseSchema = pydantic_to_marshmallow(FollowSearchResponseDTO)

GetUserFollowedSearchesSchema = create_get_many_schema(
    data_list_schema=FollowSearchResponseSchema,
    description="The searches that the user follows.",
)
