DATA_SOURCES_APPROVED_COLUMNS = [
    "name",
    "submitted_name",
    "description",
    "source_url",
    "agency_supplied",
    "supplying_entity",
    "agency_originated",
    "originating_entity",
    "agency_aggregation",
    "coverage_start",
    "coverage_end",
    "updated_at",
    "retention_schedule",
    "detail_level",
    "access_type",
    "data_portal_type",
    "record_format",
    "update_method",
    "tags",
    "readme_url",
    "scraper_url",
    "created_at",
    "airtable_source_last_modified",
    "url_status",
    "rejection_note",
    "last_approval_editor",
    "agency_described_submitted",
    "agency_described_not_in_database",
    "approval_status",
    "record_type_other",
    "data_portal_type_other",
    "data_source_request",
    "url_button",
    "tags_other",
    "access_notes",
]
ARCHIVE_INFO_APPROVED_COLUMNS = [
    "update_frequency",
    "last_cached",
]

DATA_SOURCES_MAP_COLUMN = [
    "data_source_id",
    "location_id",
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
METADATA_METHOD_NAMES = [
    "count",
    "count_subquery",
]

PAGE_SIZE = 100

GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS = [
    "location_name",
    "source_count",
    "source_change",
    "approved_requests_count",
    "approved_requests_change",
    "completed_requests_count",
    "completed_requests_change",
    "follower_count",
    "follower_change",
]
