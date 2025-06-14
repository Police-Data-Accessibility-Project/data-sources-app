from typing import Union

from marshmallow import fields, Schema, validates_schema, ValidationError

from middleware.enums import JurisdictionType
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseSchema,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.primary_resource_schemas.locations_schemas import (
    LocationInfoResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgencyInfoPutDTO,
    AgencyInfoPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_base_schemas import (
    get_name_field,
    get_jurisdiction_type_field,
    AgencyInfoBaseSchema,
    AgenciesExpandedSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


# Base Schema


class AgencyInfoPostSchema(AgencyInfoBaseSchema):
    name = get_name_field(required=True)
    jurisdiction_type = get_jurisdiction_type_field(required=True)


class AgencyInfoPutSchema(AgencyInfoBaseSchema):
    name = get_name_field(required=False)
    jurisdiction_type = get_jurisdiction_type_field(required=False)


def get_agency_info_field(
    schema: type[AgencyInfoBaseSchema],
    nested_dto_class: type[Union[AgencyInfoPutDTO, AgencyInfoPostDTO]],
) -> fields.Nested:
    return fields.Nested(
        schema,
        required=True,
        metadata={
            "description": "Information about the agency",
            "source": SourceMappingEnum.JSON,
            "nested_dto_class": nested_dto_class,
        },
    )


def validate_location_info_against_jurisdiction_type(data, jurisdiction_type):
    location_ids = data.get("location_ids")
    if location_ids is None:
        location_ids = []
    if jurisdiction_type == JurisdictionType.FEDERAL and len(location_ids) > 0:
        raise ValidationError("No locations ids allowed for jurisdiction type FEDERAL.")
    if jurisdiction_type != JurisdictionType.FEDERAL and len(location_ids) == 0:
        raise ValidationError(
            "location_id is required for non-FEDERAL jurisdiction type."
        )


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
        validate_location_info_against_jurisdiction_type(data, jurisdiction_type)


class AgenciesPutSchema(Schema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        nested_dto_class=AgencyInfoPutDTO,
    )


class AgenciesGetSchema(AgenciesExpandedSchema):
    data_sources = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "name"]),
            required=True,
            metadata=get_json_metadata(
                description="The data sources associated with the agency",
            ),
        ),
        required=True,
        metadata=get_json_metadata(
            description="The data sources associated with the agency",
        ),
    )
    locations = fields.List(
        cls_or_instance=fields.Nested(
            nested=LocationInfoResponseSchema(),
            required=True,
            metadata=get_json_metadata(
                description="The locations associated with the agency",
            ),
        ),
        required=True,
        metadata=get_json_metadata(
            description="The locations associated with the agency",
        ),
    )


class AgenciesGetByIDResponseSchema(MessageSchema):
    data = fields.Nested(
        nested=AgenciesGetSchema(),
        required=True,
        metadata={
            "description": "The result",
            "source": SourceMappingEnum.JSON,
        },
    )


class AgenciesGetManyResponseSchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=AgenciesGetSchema(),
            required=True,
            metadata={
                "description": "The list of results",
                "source": SourceMappingEnum.JSON,
            },
        ),
        required=True,
        metadata={
            "description": "The list of results",
            "source": SourceMappingEnum.JSON,
        },
    )


class RelatedAgencyByIDSchema(GetByIDBaseSchema):
    agency_id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the related agency.",
            "source": SourceMappingEnum.PATH,
        },
    )


class AgenciesRelatedLocationSchema(GetByIDBaseSchema):
    location_id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the related location.",
            "source": SourceMappingEnum.PATH,
        },
    )
