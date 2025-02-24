from typing import Union

from marshmallow import fields, Schema, validates_schema, ValidationError

from middleware.enums import JurisdictionType
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseSchema,
    LocationInfoDTO,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.primary_resource_schemas.locations_schemas import (
    LocationInfoSchema,
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
    if (
        jurisdiction_type == JurisdictionType.FEDERAL
        and data.get("location_id") is not None
    ):
        raise ValidationError("location_id must be None for jurisdiction type FEDERAL.")
    if (
        jurisdiction_type != JurisdictionType.FEDERAL
        and data.get("location_id") is None
    ):
        raise ValidationError(
            "location_id is required for non-FEDERAL jurisdiction type."
        )


class AgenciesPostPutBaseSchema(Schema):
    location_id = fields.Integer(
        required=False,
        allow_none=True,
        load_default=None,
        metadata=get_json_metadata(
            description="The id of the location associated with the agency.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )


class AgenciesPostSchema(AgenciesPostPutBaseSchema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPostSchema,
        nested_dto_class=AgencyInfoPostDTO,
    )

    @validates_schema
    def validate_location_info(self, data, **kwargs):
        jurisdiction_type = data["agency_info"].get("jurisdiction_type")
        validate_location_info_against_jurisdiction_type(data, jurisdiction_type)


class AgenciesPutSchema(AgenciesPostPutBaseSchema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        nested_dto_class=AgencyInfoPutDTO,
    )

    @validates_schema
    def validate_location_info(self, data, **kwargs):
        # Modified from PostSchema to account for the fact that
        # jurisdiction type may not be specified in a Put request
        jurisdiction_type = data["agency_info"].get("jurisdiction_type", None)
        if jurisdiction_type is None and data.get("location_info") is None:
            # location info is not being updated
            return
        if jurisdiction_type is None and data.get("location_info") is not None:
            raise ValidationError(
                "jurisdiction_type is required if location_info is provided."
            )

        validate_location_info_against_jurisdiction_type(data, jurisdiction_type)


class AgenciesGetSchema(AgenciesExpandedSchema):
    data_sources = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "submitted_name"]),
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
