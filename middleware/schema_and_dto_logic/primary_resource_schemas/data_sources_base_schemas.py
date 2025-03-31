from marshmallow import Schema, fields

from database_client.enums import (
    AgencyAggregation,
    DetailLevel,
    AccessType,
    UpdateMethod,
    RetentionSchedule,
    URLStatus,
    ApprovalStatus,
)
from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseSchema
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourceBaseSchema(Schema):
    """
    This schema correlates with the data_source table in the database
    """

    name = fields.String(
        metadata=get_json_metadata(
            "The name of the data source concatenated with the state iso.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        required=True,
    )
    description = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(
            description="Information to give clarity and confidence about what this source is, how it was "
            "processed, and whether the person reading the description might want to use it. "
            "Especially important if the source is difficult to preview or categorize.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )

    source_url = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(
            "A URL where these records can be found or are referenced.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    agency_supplied = fields.Boolean(
        allow_none=True,
        metadata=get_json_metadata(
            'Is the relevant Agency also the entity supplying the data? This may be "no" if the Agency or local '
            "government contracted with a third party to publish this data, or if a third party was the original "
            "record-keeper.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    supplying_entity = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If the Agency didn't publish this, who did?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    agency_originated = fields.Boolean(
        allow_none=True,
        metadata=get_json_metadata(
            'Is the relevant Agency also the original record-keeper? This is usually "yes", unless a third party '
            "collected data about a police Agency.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    agency_aggregation = fields.Enum(
        enum=AgencyAggregation,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "If present, the Data Source describes multiple agencies.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        allow_none=True,
    )
    coverage_start = fields.Date(
        allow_none=True,
        metadata=get_json_metadata(
            "The start date of the data source's coverage, in the format YYYY-MM-DD.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        format="iso",
    )
    coverage_end = fields.Date(
        allow_none=True,
        metadata=get_json_metadata(
            "The end date of the data source's coverage, in the format YYYY-MM-DD.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
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
            "Is this an individual record, an aggregated set of records, or a summary without underlying data?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    access_types = fields.List(
        fields.Enum(
            enum=AccessType,
            by_value=fields.Str,
            metadata=get_json_metadata(
                "The ways the data source can be accessed. Editable only by admins.",
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "The ways the data source can be accessed. Editable only by admins.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    data_portal_type = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "The data portal type of the data source.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    record_formats = fields.List(
        fields.String(
            metadata=get_json_metadata(
                "What formats the data source can be obtained in.",
                csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "What formats the data source can be obtained in.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    update_method = fields.Enum(
        enum=UpdateMethod,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata(
            "How is the data source updated?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    tags = fields.List(
        fields.String(
            allow_none=True,
            metadata=get_json_metadata(
                "Are there any keyword descriptors which might help people find this in a search? Try to limit tags to information which can't be contained in other properties."
            ),
        ),
        metadata=get_json_metadata(
            "Are there any keyword descriptors which might help people find this in a search? Try to limit tags to information which can't be contained in other properties.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        allow_none=True,
    )
    readme_url = fields.String(
        metadata=get_json_metadata(
            "A URL where supplementary information about the source is published.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        allow_none=True,
    )
    originating_entity = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Who is the originator of the data source?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    retention_schedule = fields.Enum(
        enum=RetentionSchedule,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "How long are records kept? Are there published guidelines regarding how long important information must remain accessible for future use? Editable only by admins.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
        allow_none=True,
    )
    id = fields.Integer(
        required=True,
        metadata=get_json_metadata("The id associated with the data source"),
    )
    scraper_url = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "URL for the webscraper that produces this source",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    created_at = fields.DateTime(
        metadata=get_json_metadata("The date and time the data source was created."),
    )
    submission_notes = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "What are you trying to learn? Are you trying to answer a specific question, or complete a specific project? Is there anything you've already tried?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    rejection_note = fields.String(
        allow_none=True, metadata=get_json_metadata("Why the note was rejected.")
    )
    last_approval_editor = fields.Integer(
        allow_none=True,
        metadata=get_json_metadata(
            "User id of the user who provided approval for the data source."
        ),
    )
    submitter_contact_info = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Contact information for the individual who provided the data source",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    agency_described_not_in_database = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If the agency associated is not in the database, why?",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    data_portal_type_other = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "What unconventional data portal this data source is derived from",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
    data_source_request = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Airtable UID of the associated data source request"
        ),
    )
    broken_source_url_as_of = fields.DateTime(
        allow_none=True,
        format="iso",
        metadata=get_json_metadata("When the url was marked as broken."),
    )
    access_notes = fields.String(
        metadata=get_json_metadata(
            "How the source can be accessed,",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
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
    last_approval_editor_old = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Former identifier of who provided approval for the data source."
        ),
    )


class DataSourceExpandedSchema(DataSourceBaseSchema):
    record_type_name = fields.Enum(
        enum=RecordTypes,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata(
            "The record type of the data source.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )


class DataSourcesMapResponseInnerSchema(Schema):
    data_source_id = fields.Integer(
        metadata=get_json_metadata("The id of the data source")
    )
    name = fields.String(metadata=get_json_metadata("The name of the data source"))
    location_id = fields.Integer(
        metadata=get_json_metadata("The id of the associated location")
    )
    agency_id = fields.Integer(
        metadata=get_json_metadata("The id of the associated agency")
    )
    agency_name = fields.String(
        metadata=get_json_metadata("The name of the associated agency")
    )
    state_iso = fields.String(
        metadata=get_json_metadata("The ISO code of the state"),
    )
    municipality = fields.String(
        metadata=get_json_metadata("The name of the municipality"), allow_none=True
    )
    county_name = fields.String(
        metadata=get_json_metadata("The name of the county"), allow_none=True
    )
    record_type = fields.String(metadata=get_json_metadata("The type of the record"))
    lat = fields.Float(metadata=get_json_metadata("The latitude of the data source"))
    lng = fields.Float(metadata=get_json_metadata("The longitude of the data source"))


class DataSourceRejectSchema(GetByIDBaseSchema):
    rejection_note = fields.String(
        metadata=get_json_metadata("Why the note was rejected.")
    )
