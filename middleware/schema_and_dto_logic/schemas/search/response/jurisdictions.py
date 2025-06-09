from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.schemas.search.response.outer import (
    SearchResultsOuterSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class SearchResponseJurisdictionsWrapperSchema(Schema):
    federal = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the federal jurisdiction."),
    )
    state = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the state jurisdiction."),
    )
    county = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the county jurisdiction."),
    )
    locality = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the locality jurisdiction."),
    )
