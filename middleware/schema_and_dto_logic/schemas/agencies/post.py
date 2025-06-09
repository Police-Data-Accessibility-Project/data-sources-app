from marshmallow import Schema, fields, validates_schema, ValidationError

from middleware.enums import JurisdictionType
from middleware.schema_and_dto_logic.dtos.agencies.post import AgencyInfoPostDTO
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.schemas.agencies.helpers import (
    get_agency_info_field,
)
from middleware.schema_and_dto_logic.schemas.agencies.info.post import (
    AgencyInfoPostSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class AgenciesPostSchema(Schema):
    agency_info = get_agency_info_field(
        schema=AgencyInfoPostSchema,
        nested_dto_class=AgencyInfoPostDTO,
    )
    location_ids = fields.List(
        fields.Integer(
            required=False,
            allow_none=True,
            load_default=None,
            metadata=get_json_metadata(
                description="The ids of locations associated with the agency.",
                csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
            ),
        ),
        metadata=get_json_metadata(
            description="The ids of locations associated with the agency.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )

    @validates_schema
    def validate_location_info(self, data, **kwargs):
        jurisdiction_type = data["agency_info"].get("jurisdiction_type")
        location_ids = data.get("location_ids")
        if location_ids is None:
            location_ids = []
        if jurisdiction_type == JurisdictionType.FEDERAL and len(location_ids) > 0:
            raise ValidationError(
                "No locations ids allowed for jurisdiction type FEDERAL."
            )
        if jurisdiction_type != JurisdictionType.FEDERAL and len(location_ids) == 0:
            raise ValidationError(
                "location_id is required for non-FEDERAL jurisdiction type."
            )
