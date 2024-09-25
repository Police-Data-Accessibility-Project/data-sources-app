from marshmallow import Schema, fields

from database_client.enums import RecordType
from middleware.enums import URLStatus
from utilities.enums import SourceMappingEnum


# TODO: Create schema test that checks that these all exist in the Data Sources table
class DataSourcePostSchema(Schema):
    # name = fields.Str(required=True)
    submitted_name = fields.Str(
        required=True,
        metadata={
            "description": "The name of the data source.",
            "source": SourceMappingEnum.JSON,
        },
    )
    description = fields.Str(
        allow_none=True,
        metadata={
            "description": "The description of the data source.",
            "source": SourceMappingEnum.JSON,
        },
    )
    record_type = fields.Str(
        enum=RecordType,
        by_value=fields.Str,
        metadata={
            "description": "What kind of data is accessible from this source?",
            "source": SourceMappingEnum.JSON,
        }
    )  # Enum
    source_url = fields.Str(
        allow_none=True,
        metadata={
            "description": "A URL where these records can be found or are referenced.",
            "source": SourceMappingEnum.JSON,
        }
    )
    agency_supplied = fields.Bool(
        load_default=False,
        metadata={
            "description": "Whether the data source is supplied by the agency.",
            "source": SourceMappingEnum.JSON,
        }
    )
    # TODO: The below and above might be somewhat redundant
    supplying_entity = fields.Str(
        allow_none=True,
        metadata={
            "description": "The name of the entity that supplies the data source, if not the agency.",
            "source": SourceMappingEnum.JSON,
        }
    )
    agency_originated = fields.Bool(
        load_default=False,
        metadata={
            "description": "Whether the agency supplying is also the original record-keeper.",
        }
    )
    agency_aggregation = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "If present, the Data Sources describes multiple agencies.",
            "source": SourceMappingEnum.JSON,
        }
    )
    coverage_start = fields.Date(
        allow_none=True,
        format="%Y-%m-%d",
        metadata={
            "description": "The start date of the data source, in the format YYYY-DD-MM.",
            "source": SourceMappingEnum.JSON,
        }
    )
    coverage_end = fields.Date(
        allow_none=True,
        format="%Y-%m-%d",
        metadata={
            "description": "The end date of the data source, in the format YYYY-DD-MM.",
            "source": SourceMappingEnum.JSON,
        }
    )
    source_last_updated = fields.Date(
        allow_none=True,
        format="%Y-%m-%d",
        metadata={
            "description": "The date the data source was last updated, in the format YYYY-DD-MM.",
            "source": SourceMappingEnum.JSON,
        }
    )
    detail_level = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "The detail level of the data source: whether this is an individual record, an aggregated set of records, or a summary without underlying data.",
            "source": SourceMappingEnum.JSON,
        }
    )
    number_of_records_available = fields.Int(
        allow_none=True,
        metadata={
            "description": "How many similar pieces of information are available at this source?",
            "source": SourceMappingEnum.JSON,
        }
    )
    size = fields.Str(
        metadata={
            "description": "The size of the data source, if downloaded.",
            "source": SourceMappingEnum.JSON,
        }
    )
    access_type = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "The type of access available from this source.",
            "source": SourceMappingEnum.JSON,
        }
    )
    record_download_option_provided = fields.Bool(
        load_default=False,
        metadata={
            "description": "Whether the source provides record download options.",
            "source": SourceMappingEnum.JSON,
        }
    )
    data_portal_type = fields.Str(
        allow_none=True,
        metadata={
            "description": "Some data is published via a standard third-party portal, typically named somewhere on the page.",
            "source": SourceMappingEnum.JSON,
        }
    )
    record_format = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "The format(s) of the data source.  Array items can have values such as CSV, JSON, XML, RDF, RSS, HTML table and others.",
            "source": SourceMappingEnum.JSON,
        }
    )
    update_method = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "How is the data source updated? Are records replaced (Overwrite) or added (Insert)?",
            "source": SourceMappingEnum.JSON,
        }
    )
    tags = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "Tags associated with the data source.",
            "source": SourceMappingEnum.JSON,
        }
    )  # Array
    readme_url = fields.Str()
    originating_entity = fields.Str()
    retention_schedule = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "The retention schedule of the data source. How long are records kept? Are there published guidelines regarding how long important information must remain accessible for future use?",
            "source": SourceMappingEnum.JSON,
        }
    )
    airtable_uid = fields.Str(required=True)
    scraper_url = fields.Str()
    data_source_created = fields.DateTime()
    airtable_source_last_modified = fields.DateTime()
    url_broken = fields.Bool()
    submission_notes = fields.Str()
    rejection_note = fields.Str()
    last_approval_editor = fields.Str()
    submitter_contact_info = fields.Str()
    agency_described_submitted = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "To which criminal legal system agency or agencies does this Data Source refer?",
            "source": SourceMappingEnum.JSON,
        }
    )
    agency_described_not_in_database = fields.Str()
    approved = fields.Bool()
    record_type_other = fields.Str()
    data_portal_type_other = fields.Str()
    private_access_instructions = fields.Str()
    records_not_online = fields.Bool()
    data_source_request = fields.Str()
    url_button = fields.Str()
    tags_other = fields.Str(
        allow_none=True,
        metadata={
            "description": "Other tags associated with the data source.",
            "source": SourceMappingEnum.JSON,
        }
    )
    broken_source_url_as_of = fields.Date(
        allow_none=True,
        format="%Y-%m-%d",
        metadata={
            "description": "The date the data source was determined to be broken, in the format YYYY-DD-MM.",
            "source": SourceMappingEnum.JSON,
        }
    )
    access_notes = fields.Str(
        allow_none=True,
        metadata={
            "description": "Is anything special required to access the data?",
            "source": SourceMappingEnum.JSON,
        }
    )
    url_status = fields.Enum(
        enum=URLStatus,
        allow_none=True,
        load_default=URLStatus.OK,
        by_value=fields.Str(),
        metadata={
            "description": "The status of the source_url, including options like ok , none found , broken",
            "source": SourceMappingEnum.JSON,
        }
    )
    approval_status = fields.Str()
    record_type_id = fields.Int()
