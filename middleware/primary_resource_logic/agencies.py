from dataclasses import dataclass

from flask import Response
from marshmallow import Schema, fields, validate

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetManyBaseDTO,
    GetByIDBaseDTO,
)
from middleware.enums import Relations, JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.response_schemas import GetManyResponseSchemaBase
from utilities.enums import SourceMappingEnum


class AgenciesPostSchema(Schema):
    submitted_name = fields.Str(
        required=True,
        metadata={
            "description": "The name of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    homepage_url = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The URL of the agency's homepage.",
            "source": SourceMappingEnum.JSON,
        },
    )
    jurisdiction_type = fields.Enum(
        required=False,
        enum=JurisdictionType,
        by_value=fields.Str,
        load_default=JurisdictionType.NONE,
        metadata={
            "description": "The highest level of jurisdiction of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    state_iso = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The 2 letter ISO code of the state in which the agency is located.",
            "source": SourceMappingEnum.JSON,
        },
        validate=validate.Length(2),
    )
    county_fips = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The unique 5-digit FIPS code of the county in which the agency is located. "
            "Does not apply to state or federal agencies.",
            "source": SourceMappingEnum.JSON,
        },
        validate=validate.Length(5),
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
    airtable_uid = fields.Str(
        required=False,
        metadata={
            "description": "The Airtable UID of the agency.",
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
        allow_none=True,
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
        allow_none=True,
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
    locality_name = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The name of the locality in which the agency is located.",
            "source": SourceMappingEnum.JSON,
        },
    )


@dataclass
class AgenciesPostDTO:
    submitted_name: str
    homepage_url: str
    jurisdiction_type: JurisdictionType
    state_iso: str
    county_fips: str
    lat: float
    lng: float
    defunct_year: str
    airtable_uid: str
    agency_type: AgencyType
    multi_agency: bool
    zip_code: str
    no_web_presence: bool
    approved: bool
    rejection_reason: str
    last_approval_editor: str
    submitter_contact: str
    locality_name: str


class AgenciesGetSchema(AgenciesPostSchema):
    name = fields.Str(
        required=False,
        metadata={
            "description": "The name of the agency. If a state is provided, "
            "concatenates `submitted_name` + ` - ` + `state_iso` "
            "to help differentiate agencies with similar names.",
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
    count_data_sources = fields.Int(
        required=False,
        metadata={
            "description": "The number of data sources associated with the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    data_sources = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The list of data sources associated with the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    airtable_agency_last_modified = fields.DateTime(
        required=False,
        format="rfc",
        metadata={
            "description": "When the agency was last modified",
            "source": SourceMappingEnum.JSON,
        },
    )
    data_sources_last_updated = fields.DateTime(
        required=False,
        allow_none=True,
        format="rfc",
        metadata={
            "description": "When the data sources were last updated",
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
    county_airtable_uid = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The Airtable UID of the county.",
            "source": SourceMappingEnum.JSON,
        },
    )
    locality_id = fields.Int(
        required=False,
        allow_none=True,
        metadata={
            "description": "The ID of the locality in which the agency is located.",
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


def create_agency(
    db_client: DatabaseClient, dto: EntryDataRequestDTO, access_info: AccessInfo
) -> Response:
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.create_agency,
        ),
        entry=dto.entry_data,
    )


def update_agency(
    db_client: DatabaseClient,
    dto: EntryDataRequestDTO,
    access_info: AccessInfo,
    agency_id: str,
) -> Response:
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.update_agency,
        ),
        entry=dto.entry_data,
        entry_id=agency_id,
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
