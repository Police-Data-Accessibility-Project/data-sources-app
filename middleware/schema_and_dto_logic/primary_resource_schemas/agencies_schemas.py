from dataclasses import dataclass
from typing import Optional, Union

from marshmallow import fields, Schema, validate, validates_schema, ValidationError

from database_client.enums import LocationType
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
    GetManyResponseSchemaBase,
)
from utilities.enums import SourceMappingEnum


def get_submitted_name_field(required: bool) -> fields.Str:
    return fields.Str(
        required=required,
        metadata={
            "description": "The name of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


def get_jurisdiction_type_field(required: bool) -> fields.Enum:
    return fields.Enum(
        required=required,
        enum=JurisdictionType,
        by_value=fields.Str,
        metadata={
            "description": "The highest level of jurisdiction of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


class AgencyInfoBaseSchema(Schema):
    homepage_url = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The URL of the agency's homepage.",
            "source": SourceMappingEnum.JSON,
        },
    )
    lat = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The latitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
        },
    )
    lng = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The longitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
        },
    )
    defunct_year = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "If present, denotes an agency which has defunct but may still have relevant records.",
            "source": SourceMappingEnum.JSON,
        },
    )
    agency_type = fields.Enum(
        required=False,
        enum=AgencyType,
        by_value=fields.Str,
        allow_none=True,
        load_default=AgencyType.NONE,
        metadata={
            "description": "The type of agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    multi_agency = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether the agency is a multi-agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    zip_code = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The zip code of the agency's location.",
            "source": SourceMappingEnum.JSON,
        },
        # TODO: Re-enable when all zip codes are of expected length
        # validate=validate.Length(min=5),
    )
    no_web_presence = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "True when an agency does not have a dedicated website.",
            "source": SourceMappingEnum.JSON,
        },
    )
    approved = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether the agency is approved.",
            "source": SourceMappingEnum.JSON,
        },
    )
    rejection_reason = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The reason the agency was rejected.",
            "source": SourceMappingEnum.JSON,
        },
    )
    last_approval_editor = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "The user who last approved or rejected the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitter_contact = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The contact information of the user who submitted the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


class AgencyInfoPostSchema(AgencyInfoBaseSchema):
    submitted_name = get_submitted_name_field(required=True)
    airtable_uid = fields.Str(
        required=True,
        metadata={
            "description": "The Airtable UID of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    jurisdiction_type = get_jurisdiction_type_field(required=True)


class AgencyInfoPutSchema(AgencyInfoBaseSchema):
    submitted_name = get_submitted_name_field(required=False)
    jurisdiction_type = get_jurisdiction_type_field(required=False)


STATE_ISO_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The 2 letter ISO code of the state in which the agency is located. Does not apply to federal agencies",
        "source": SourceMappingEnum.JSON,
    },
    validate=validate.Length(2),
)
COUNTY_FIPS_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The unique 5-digit FIPS code of the county in which the agency is located."
        "Does not apply to state or federal agencies.",
        "source": SourceMappingEnum.JSON,
    },
    validate=validate.Length(5),
)
LOCALITY_NAME_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The name of the locality in which the agency is located.",
        "source": SourceMappingEnum.JSON,
    },
)


class LocationInfoSchema(Schema):
    type = fields.Enum(
        required=True,
        enum=LocationType,
        by_value=fields.Str,
        metadata={
            "description": "The type of location. ",
            "source": SourceMappingEnum.JSON,
        },
    )
    state_iso = STATE_ISO_FIELD
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD

    @validates_schema
    def validate_location_fields(self, data, **kwargs):
        location_type = data.get("type")

        if location_type == LocationType.STATE:
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type STATE.")
            if (
                data.get("county_fips") is not None
                or data.get("locality_name") is not None
            ):
                raise ValidationError(
                    "county_fips and locality_name must be None for location type STATE."
                )

        elif location_type == LocationType.COUNTY:
            if data.get("county_fips") is None:
                raise ValidationError(
                    "county_fips is required for location type COUNTY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type COUNTY.")
            if data.get("locality_name"):
                raise ValidationError(
                    "locality_name must be None for location type COUNTY."
                )

        elif location_type == LocationType.LOCALITY:
            if data.get("locality_name") is None:
                raise ValidationError(
                    "locality_name is required for location type CITY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type CITY.")
            if data.get("county_fips") is None:
                raise ValidationError("county_fips is required for location type CITY.")


@dataclass
class AgencyInfoPutDTO:
    submitted_name: Optional[str] = None
    jurisdiction_type: Optional[JurisdictionType] = None
    agency_type: AgencyType = AgencyType.NONE
    multi_agency: Optional[bool] = False
    no_web_presence: Optional[bool] = False
    approved: Optional[bool] = False
    homepage_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    defunct_year: Optional[str] = None
    zip_code: Optional[str] = None
    rejection_reason: Optional[str] = None
    last_approval_editor: Optional[str] = None
    submitter_contact: Optional[str] = None


@dataclass
class AgencyInfoPostDTO:
    submitted_name: str
    jurisdiction_type: JurisdictionType
    airtable_uid: str
    agency_type: AgencyType
    multi_agency: bool = False
    no_web_presence: bool = False
    approved: bool = False
    homepage_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    defunct_year: Optional[str] = None
    zip_code: Optional[str] = None
    rejection_reason: Optional[str] = None
    last_approval_editor: Optional[str] = None
    submitter_contact: Optional[str] = None


@dataclass
class LocationInfoDTO:
    type: LocationType
    state_iso: str
    county_fips: Optional[str] = None
    locality_name: Optional[str] = None


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
        and data.get("location_info") is not None
    ):
        raise ValidationError(
            "location_info must be None for jurisdiction type FEDERAL."
        )
    if (
        jurisdiction_type != JurisdictionType.FEDERAL
        and data.get("location_info") is None
    ):
        raise ValidationError(
            "location_info is required for non-FEDERAL jurisdiction type."
        )


class AgenciesPostPutBaseSchema(Schema):
    location_info = fields.Nested(
        LocationInfoSchema,
        required=False,
        allow_none=True,
        metadata={
            "description": "The locational information of the agency. Must be None if agency is of jurisdiction_type `federal`",
            "source": SourceMappingEnum.JSON,
            "nested_dto_class": LocationInfoDTO,
        },
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


@dataclass
class AgenciesPostDTO:
    agency_info: AgencyInfoPostDTO
    location_info: Optional[LocationInfoDTO] = None


@dataclass
class AgenciesPutDTO:
    agency_info: AgencyInfoPutDTO
    location_info: Optional[LocationInfoDTO] = None


class AgenciesGetSchema(AgencyInfoBaseSchema):
    airtable_uid = fields.Str(
        required=True,
        metadata={
            "description": "The Airtable UID of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitted_name = get_submitted_name_field(required=True)
    jurisdiction_type = get_jurisdiction_type_field(required=True)
    name = fields.Str(
        required=False,
        metadata={
            "description": "The name of the agency. If a state is provided, "
            "concatenates `submitted_name` + ` - ` + `state_iso` "
            "to help differentiate agencies with similar names.",
            "source": SourceMappingEnum.JSON,
        },
    )
    state_iso = STATE_ISO_FIELD
    state_name = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The name of the state in which the agency is located. Does not apply to federal agencies",
            "source": SourceMappingEnum.JSON,
        },
    )
    county_name = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The name of the county in which the agency is located.",
            "source": SourceMappingEnum.JSON,
        },
    )
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD
    airtable_agency_last_modified = fields.DateTime(
        required=False,
        format="iso",
        metadata={
            "description": "When the agency was last modified",
            "source": SourceMappingEnum.JSON,
        },
    )
    agency_created = fields.DateTime(
        required=False,
        format="iso",
        metadata={
            "description": "When the agency was created",
            "source": SourceMappingEnum.JSON,
        },
    )


class AgenciesGetByIDResponseSchema(MessageSchema):
    data = fields.Nested(
        nested=AgenciesGetSchema,
        required=True,
        metadata={
            "description": "The result",
            "source": SourceMappingEnum.JSON,
        },
    )


class AgenciesGetManyResponseSchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=AgenciesGetSchema,
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
