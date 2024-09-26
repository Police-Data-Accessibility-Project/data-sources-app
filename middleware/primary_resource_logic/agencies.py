from collections import namedtuple
from dataclasses import dataclass, asdict
from http import HTTPStatus
from typing import Optional, Union

import requests
from flask import Response, request
from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import RelationRoleParameters
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry, PostLogic
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetManyBaseDTO,
    GetByIDBaseDTO,
)
from middleware.enums import Relations, JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
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
        validate=validate.Length(5),
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
    last_approval_editor = fields.Str(
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
            if data.get("county_fips") is not None or data.get("locality_name") is not None:
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
    dto_class: type[Union[AgencyInfoPutDTO, AgencyInfoPostDTO]],
) -> fields.Nested:
    return fields.Nested(
        schema,
        required=True,
        metadata={
            "description": "Information about the agency",
            "source": SourceMappingEnum.JSON,
            "nested_dto_class": dto_class,
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
    agency_info = get_agency_info_field(
        schema=AgencyInfoPostSchema,
        dto_class=AgencyInfoPostDTO,
    )

    @validates_schema
    def validate_location_info(self, data, **kwargs):
        jurisdiction_type = data["agency_info"].get("jurisdiction_type")
        validate_location_info_against_jurisdiction_type(data, jurisdiction_type)


class AgenciesPutSchema(AgenciesPostPutBaseSchema):
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        dto_class=AgencyInfoPutDTO,
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
        format="rfc",
        metadata={
            "description": "When the agency was last modified",
            "source": SourceMappingEnum.JSON,
        },
    )
    agency_created = fields.DateTime(
        required=False,
        format="rfc",
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


def get_agencies(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetManyBaseDTO
) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    return get_many(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agencies",
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
        ),
        page=dto.page,
    )


def get_agency_by_id(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetByIDBaseDTO
) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
        ),
        id=dto.resource_id,
        id_column_name="airtable_uid",
    )


class InvalidLocationError(Exception):
    pass


def get_location_id(db_client: DatabaseClient, location_info: LocationInfoDTO):

    location_info_dict = asdict(location_info)
    location_info_where_mappings = WhereMapping.from_dict(location_info_dict)
    # Get location id
    results = db_client.get_location_id(where_mappings=location_info_where_mappings)
    location_exists = len(results) > 0
    if location_exists:
        return results[0]["id"]
    _raise_if_not_locality(location_info, location_info_dict)

    # In the case of a nonexistent locality, this can be added,
    # provided the rest of the location is valid
    county_id = _get_county_id(db_client, location_info_dict)

    # If this exists, locality does not yet exist in database and should be added. Add and return location id
    db_client.create_locality(
        column_value_mappings={
            "name": location_info.locality_name,
            "county_id": county_id,
        }
    )
    return db_client.get_location_id(where_mappings=location_info_where_mappings)[0][
        "id"
    ]


def _raise_if_not_locality(location_info, location_info_dict):
    if location_info.type != LocationType.LOCALITY:
        # Invalid location
        raise InvalidLocationError(f"{location_info_dict} is not a valid location")


def _get_county_id(db_client, location_info_dict) -> int:
    county_dict = {
        "county_fips": location_info_dict["county_fips"],
        "state_iso": location_info_dict["state_iso"],
        "type": LocationType.COUNTY,
    }
    results = db_client._select_from_single_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["county_id"],
        where_mappings=WhereMapping.from_dict(county_dict),
    )
    location_without_locality_exists = len(results) > 0
    if not location_without_locality_exists:
        raise InvalidLocationError(
            f"{location_info_dict} is not a valid location: {county_dict} is not a valid county"
        )
    return results[0]["county_id"]


def validate_and_add_location_info(
    db_client: DatabaseClient, entry_data: dict, location_info: LocationInfoDTO
):
    """
    Checks that location provided is a valid one, and returns the associated location id
    In the case of a locality which does not yet exist, adds it and returns the location id
    :param db_client:
    :param entry_data: Modified in-place
    :param location_info:
    :return:
    """
    location_id = get_location_id(db_client, location_info)
    entry_data["location_id"] = location_id


def create_agency(
    db_client: DatabaseClient, dto: AgenciesPostDTO, access_info: AccessInfo
) -> Response:
    entry_data = asdict(dto.agency_info)
    deferred_function = optionally_get_location_info_deferred_function(
        db_client=db_client,
        jurisdiction_type=dto.agency_info.jurisdiction_type,
        entry_data=entry_data,
        location_info=dto.location_info,
    )

    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.create_agency,
        ),
        entry=entry_data,
        pre_insertion_function_with_parameters=deferred_function,
    )


def optionally_get_location_info_deferred_function(
    db_client: DatabaseClient,
    jurisdiction_type: JurisdictionType,
    entry_data: dict,
    location_info: LocationInfoDTO,
):
    if jurisdiction_type == JurisdictionType.FEDERAL:
        deferred_function = None
    else:
        deferred_function = DeferredFunction(
            function=validate_and_add_location_info,
            db_client=db_client,
            entry_data=entry_data,
            location_info=location_info,
        )
    return deferred_function


def update_agency(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    agency_id: str,
) -> Response:
    AgenciesPutSchema().load(request.json)
    entry_data = request.json.get("agency_info")
    location_info = request.json.get("location_info")
    if location_info is not None:
        jurisdiction_type = entry_data.get("jurisdiction_type")
        deferred_function = optionally_get_location_info_deferred_function(
            db_client=db_client,
            jurisdiction_type=jurisdiction_type,
            entry_data=entry_data,
            location_info=location_info,
        )
    else:
        deferred_function = None

    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.update_agency,
        ),
        entry=entry_data,
        entry_id=agency_id,
        pre_update_method_with_parameters=deferred_function,
    )


def delete_agency(
    db_client: DatabaseClient, access_info: AccessInfo, agency_id: str
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.delete_agency,
        ),
        id_info=IDInfo(id_column_name="airtable_uid", id_column_value=agency_id),
    )
