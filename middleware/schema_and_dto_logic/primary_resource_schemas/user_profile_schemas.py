from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.schema_helpers import create_get_many_schema
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import RecordCategories


class GetUserRecentSearchesInnerSchema(Schema):
    state_iso = fields.Str(
        required=True,
        metadata=get_json_metadata("The state of the search."),
    )
    county_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The county of the search, if any."),
    )
    locality_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The locality of the search, if any."),
    )
    location_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of location of the search")
    )
    record_categories = fields.List(
        fields.Enum(
            enum=RecordCategories,
            by_value=fields.Str,
            metadata=get_json_metadata(
                "The record categories of the search."
            ),
        ),
        required=True,
        metadata=get_json_metadata("The record categories of the search."),
    )


GetUserRecentSearchesOuterSchema = create_get_many_schema(
    data_list_schema=GetUserRecentSearchesInnerSchema(),
    description="The list of recent searches for the user",
)