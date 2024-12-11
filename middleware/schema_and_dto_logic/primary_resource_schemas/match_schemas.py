from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class AgencyMatchInnerSchema(Schema):
    name = fields.String(metadata=get_json_metadata("The name of the agency"))
    state = fields.String(metadata=get_json_metadata("The state of the agency"))
    county = fields.String(metadata=get_json_metadata("The county of the agency"))
    locality = fields.String(metadata=get_json_metadata("The locality of the agency"))


class AgencyMatterOuterSchema(Schema):
    entries = fields.List(
        fields.Nested(AgencyMatchInnerSchema()),
        metadata=get_json_metadata("The proposed agencies to find matches for."),
    )
