from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from marshmallow import Schema, fields

from database_client.enums import (
    LocationType,
    DetailLevel,
    AccessType,
    RetentionSchedule,
    URLStatus,
    ApprovalStatus,
    AgencyAggregation,
    UpdateMethod,
)
from middleware.enums import RecordType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    EntryCreateUpdateRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import (
    AgenciesGetSchema,
)
from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


@dataclass
class DataSourceEntryDataPostDTO:
    submitted_name: str
    description: Optional[str] = None
    approval_status: Optional[ApprovalStatus] = None
    source_url: Optional[str] = None
    agency_supplied: Optional[bool] = None
    supplying_entity: Optional[str] = None
    agency_originated: Optional[bool] = None
    agency_aggregation: Optional[AgencyAggregation] = None
    coverage_start: Optional[date] = None
    coverage_end: Optional[date] = None
    detail_level: Optional[DetailLevel] = None
    access_types: Optional[List[AccessType]] = None
    record_download_option_provided: Optional[bool] = None
    data_portal_type: Optional[str] = None
    record_formats: Optional[List[str]] = None
    update_method: Optional[str] = None
    tags: Optional[List[str]] = None
    readme_url: Optional[str] = None
    originating_entity: Optional[str] = None
    retention_schedule: Optional[RetentionSchedule] = None
    scraper_url: Optional[str] = None
    submission_notes: Optional[str] = None
    rejection_note: Optional[str] = None
    last_approval_editor: Optional[str] = None
    submitter_contact_info: Optional[str] = None
    agency_described_submitted: Optional[str] = None
    agency_described_not_in_database: Optional[str] = None
    data_portal_type_other: Optional[str] = None
    data_source_request: Optional[str] = None
    broken_source_url_as_of: Optional[date] = None
    access_notes: Optional[str] = None
    url_status: Optional[URLStatus] = None
    record_type_name: Optional[RecordType] = None


@dataclass
class DataSourcesPostDTO:
    entry_data: DataSourceEntryDataPostDTO


class DataSourceBaseSchema(Schema):
    """
    This schema correlates with the data_source table in the database
    """

    name = fields.String(
        metadata=get_json_metadata(
            "The name of the data source concatenated with the state iso."
        ),
    )
    submitted_name = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(
            "The name of the data source as originally submitted."
        ),
    )
    description = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(
            description="Information to give clarity and confidence about what this source is, how it was "
            "processed, and whether the person reading the description might want to use it. "
            "Especially important if the source is difficult to preview or categorize."
        ),
    )

    source_url = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(
            "A URL where these records can be found or are referenced."
        ),
    )
    agency_supplied = fields.Boolean(
        allow_none=True,
        metadata=get_json_metadata(
            'Is the relevant Agency also the entity supplying the data? This may be "no" if the Agency or local '
            "government contracted with a third party to publish this data, or if a third party was the original "
            "record-keeper."
        ),
    )
    supplying_entity = fields.String(
        allow_none=True,
        metadata=get_json_metadata("If the Agency didn't publish this, who did?"),
    )
    agency_originated = fields.Boolean(
        allow_none=True,
        metadata=get_json_metadata(
            'Is the relevant Agency also the original record-keeper? This is usually "yes", unless a third party '
            "collected data about a police Agency."
        ),
    )
    agency_aggregation = fields.Enum(
        enum=AgencyAggregation,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "If present, the Data Source describes multiple agencies."
        ),
        allow_none=True,
    )
    coverage_start = fields.Date(
        allow_none=True,
        metadata=get_json_metadata(
            "The start date of the data source's coverage, in the format YYYY-MM-DD."
        ),
        format="iso",
    )
    coverage_end = fields.Date(
        allow_none=True,
        metadata=get_json_metadata(
            "The end date of the data source's coverage, in the format YYYY-MM-DD."
        ),
        format="iso",
    )
    updated_at = fields.DateTime(
        allow_none=True,
        metadata=get_json_metadata(
            "The date that the data source was last updated, in the format YYYY-MM-DD."
        ),
        format="iso",
    )
    detail_level = fields.Enum(
        allow_none=True,
        enum=DetailLevel,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "Is this an individual record, an aggregated set of records, or a summary without underlying data?"
        ),
    )
    access_types = fields.List(
        fields.Enum(
            enum=AccessType,
            by_value=fields.Str,
            metadata=get_json_metadata(
                "The ways the data source can be accessed. Editable only by admins."
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "The ways the data source can be accessed. Editable only by admins."
        ),
    )
    record_download_option_provided = fields.Boolean(
        allow_none=True,
        metadata=get_json_metadata(
            "Is there a way to download the data source's records?"
        ),
    )
    data_portal_type = fields.String(
        allow_none=True,
        metadata=get_json_metadata("The data portal type of the data source."),
    )
    record_formats = fields.List(
        fields.String(
            metadata=get_json_metadata(
                "What formats the data source can be obtained in."
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata("What formats the data source can be obtained in."),
    )
    update_method = fields.Enum(
        enum=UpdateMethod,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata("How is the data source updated?"),
    )
    tags = fields.List(
        fields.String(
            allow_none=True,
            metadata=get_json_metadata(
                "Are there any keyword descriptors which might help people find this in a search? Try to limit tags to information which can't be contained in other properties."
            ),
        ),
        metadata=get_json_metadata(
            "Are there any keyword descriptors which might help people find this in a search? Try to limit tags to information which can't be contained in other properties."
        ),
        allow_none=True,
    )
    readme_url = fields.String(
        metadata=get_json_metadata(
            "A URL where supplementary information about the source is published."
        ),
        allow_none=True,
    )
    originating_entity = fields.String(
        allow_none=True,
        metadata=get_json_metadata("Who is the originator of the data source?"),
    )
    retention_schedule = fields.Enum(
        enum=RetentionSchedule,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "How long are records kept? Are there published guidelines regarding how long important information must remain accessible for future use? Editable only by admins."
        ),
        allow_none=True,
    )
    id = fields.Integer(
        required=True,
        metadata=get_json_metadata("The id associated with the data source"),
    )
    scraper_url = fields.String(
        allow_none=True,
        metadata=get_json_metadata("URL for the webscraper that produces this source"),
    )
    created_at = fields.DateTime(
        metadata=get_json_metadata("The date and time the data source was created."),
    )
    submission_notes = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "What are you trying to learn? Are you trying to answer a specific question, or complete a specific project? Is there anything you've already tried?"
        ),
    )
    rejection_note = fields.String(
        allow_none=True, metadata=get_json_metadata("Why the note was rejected.")
    )
    last_approval_editor = fields.String(
        allow_none=True,
        metadata=get_json_metadata("Who provided approval for the data source."),
    )
    submitter_contact_info = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Contact information for the individual who provided the data source"
        ),
    )
    agency_described_submitted = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "To which criminal legal systems agency or agencies does this Data Source refer?"
        ),
    )
    agency_described_not_in_database = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If the agency associated is not in the database, why?"
        ),
    )
    data_portal_type_other = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "What unconventional data portal this data source is derived from"
        ),
    )
    data_source_request = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Airtable UID of the associated data source request"
        ),
    )
    broken_source_url_as_of = fields.Date(
        allow_none=True,
        format="iso",
        metadata=get_json_metadata("When the url was marked as broken."),
    )
    access_notes = fields.String(
        metadata=get_json_metadata("How the source can be accessed,"),
        allow_none=True,
    )
    url_status = fields.Enum(
        URLStatus,
        by_value=fields.String,
        metadata=get_json_metadata("The status of the url. Editable only by admins."),
    )
    approval_status = fields.Enum(
        ApprovalStatus,
        by_value=fields.String,
        metadata=get_json_metadata(
            "The approval status of the data source. Editable only by admins."
        ),
    )
    record_type_id = fields.Integer(
        metadata=get_json_metadata(
            "The record type id associated with the data source"
        ),
        allow_none=True,
    )
    approval_status_updated_at = fields.DateTime(
        metadata=get_json_metadata(
            "The date and time the approval status was last updated"
        )
    )


class DataSourceExpandedSchema(DataSourceBaseSchema):
    record_type_name = fields.Enum(
        enum=RecordType,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata("The type of data source. Editable only by admins."),
    )


class DataSourceGetSchema(DataSourceExpandedSchema):
    """
    The schema for getting a single data source.
    Include the base schema as well as data from connected tables, including agencies and record types.
    """

    agencies = fields.List(
        fields.Nested(
            AgenciesGetSchema,
            metadata=get_json_metadata("The agencies associated with the data source."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The agencies associated with the data source."),
    )
    agency_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The agency ids associated with the data source."
            ),
        ),
        metadata=get_json_metadata("The agency ids associated with the data source."),
    )


class DataSourcesGetByIDSchema(MessageSchema):
    data = fields.Nested(
        DataSourceGetSchema,
        metadata=get_json_metadata("The result"),
    )


class DataSourcesGetManySchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceGetSchema,
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )


class DataSourcesPostSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=["id", "name", "updated_at", "created_at", "record_type_id"],
            partial=True,
        ),
        required=True,
        metadata=get_json_metadata(
            description="The data source to be created",
            nested_dto_class=DataSourceEntryDataPostDTO,
        ),
    )


class DataSourcesPutSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=[
                "name",
                "id",
                "updated_at",
                "created_at",
                "rejection_note",
                "record_type_id",
                "data_source_request",
            ]
        ),
        required=True,
        metadata=get_json_metadata("The data source to be updated"),
    )


class DataSourcesGetManyRequestSchema(GetManyRequestsBaseSchema):
    approval_status = fields.Enum(
        enum=ApprovalStatus,
        by_value=fields.String,
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The approval status of the data sources.",
            "default": "approved",
        },
    )
