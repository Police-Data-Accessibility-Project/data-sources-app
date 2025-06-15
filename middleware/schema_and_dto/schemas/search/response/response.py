from marshmallow import Schema, fields

from middleware.schema_and_dto.schemas.search.response.jurisdictions import (
    SearchResponseJurisdictionsWrapperSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class SearchResponseSchema(Schema):
    data = fields.Nested(
        SearchResponseJurisdictionsWrapperSchema(),
        metadata=get_json_metadata("The list of results"),
    )
    count = fields.Int(
        metadata=get_json_metadata("The number of results"),
    )
