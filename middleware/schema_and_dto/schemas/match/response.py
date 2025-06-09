from marshmallow import Schema, fields

from middleware.primary_resource_logic.match import AgencyMatchStatus
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

from middleware.schema_and_dto.schemas.match.location import (
    MatchAgenciesLocationSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class MatchAgenciesResultSchema(Schema):
    id = fields.Integer(metadata=get_json_metadata("The id of the agency"))
    name = fields.String(metadata=get_json_metadata("The name of the agency"))
    agency_type = fields.String(
        metadata=get_json_metadata("The type of the agency"),
        allow_none=True,
    )
    locations = fields.List(
        fields.Nested(
            MatchAgenciesLocationSchema(),
            required=False,
            metadata=get_json_metadata("The locations of the agency"),
        ),
        required=False,
        metadata=get_json_metadata("The locations of the agency"),
    )
    similarity = fields.Float(
        metadata=get_json_metadata("The similarity of the agency to the search")
    )


class MatchAgencyResponseSchema(MessageSchema):

    status = fields.Enum(
        enum=AgencyMatchStatus,
        by_value=fields.Str,
        required=True,
        metadata=get_json_metadata("The status of the match"),
    )
    agencies = fields.List(
        fields.Nested(
            MatchAgenciesResultSchema(),
            metadata=get_json_metadata("The list of results, if any"),
        ),
        required=False,
        metadata=get_json_metadata("The list of results, if any"),
    )
