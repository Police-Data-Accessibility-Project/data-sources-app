from middleware.models import Agency, DataRequest, DataSource, TestTable

AGENCY_APPROVED_COLUMNS = [
    "homepage_url",
    "count_data_sources",
    "agency_type",
    "multi_agency",
    "submitted_name",
    "jurisdiction_type",
    "state_iso",
    "municipality",
    "zip_code",
    "county_fips",
    "county_name",
    "lat",
    "lng",
    "data_sources",
    "no_web_presence",
    "airtable_agency_last_modified",
    "data_sources_last_updated",
    "approved",
    "rejection_reason",
    "last_approval_editor",
    "agency_created",
    "county_airtable_uid",
    "defunct_year",
]
DATA_SOURCES_APPROVED_COLUMNS = [
    "name",
    "submitted_name",
    "description",
    "record_type",
    "source_url",
    "agency_supplied",
    "supplying_entity",
    "agency_originated",
    "originating_entity",
    "agency_aggregation",
    "coverage_start",
    "coverage_end",
    "source_last_updated",
    "retention_schedule",
    "detail_level",
    "number_of_records_available",
    "size",
    "access_type",
    "data_portal_type",
    "record_format",
    "update_method",
    "tags",
    "readme_url",
    "scraper_url",
    "data_source_created",
    "airtable_source_last_modified",
    "url_status",
    "rejection_note",
    "last_approval_editor",
    "agency_described_submitted",
    "agency_described_not_in_database",
    "approval_status",
    "record_type_other",
    "data_portal_type_other",
    "records_not_online",
    "data_source_request",
    "url_button",
    "tags_other",
    "access_notes",
]
ARCHIVE_INFO_APPROVED_COLUMNS = [
    "update_frequency",
    "last_cached",
]
DATA_SOURCES_OUTPUT_COLUMNS = (
    DATA_SOURCES_APPROVED_COLUMNS + ARCHIVE_INFO_APPROVED_COLUMNS + ["agency_name"]
)
RESTRICTED_DATA_SOURCE_COLUMNS = [
    "rejection_note",
    "data_source_request",
    "approval_status",
    "airtable_uid",
    "airtable_source_last_modified",
]
DATA_SOURCES_MAP_COLUMN = [
    "data_source_id",
    "name",
    "agency_id",
    "agency_name",
    "state_iso",
    "municipality",
    "county_name",
    "record_type",
    "lat",
    "lng",
]
RESTRICTED_COLUMNS = [
    "rejection_note",
    "data_source_request",
    "approval_status",
    "airtable_uid",
    "airtable_source_last_modified",
]

PAGE_SIZE = 100

TABLE_REFERENCE = {
    "agencies": Agency,
    "data_requests": DataRequest,
    "data_sources": DataSource,
    "test_table": TestTable,
}