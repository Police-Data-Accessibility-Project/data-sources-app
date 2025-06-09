from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.schemas.search.response.inner import (
    SearchResultsInnerSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class SearchResultsOuterSchema(Schema):
    results = fields.List(
        fields.Nested(
            SearchResultsInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )
    count = fields.Int(
        required=True,
        metadata=get_json_metadata("The number of results"),
    )
