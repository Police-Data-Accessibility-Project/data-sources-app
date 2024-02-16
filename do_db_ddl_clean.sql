CREATE TABLE if not exists access_tokens (
    id bigint NOT NULL,
    token character varying,
    expiration_date timestamp with time zone NOT NULL
);

CREATE TABLE if not exists agencies (
    name character varying NOT NULL,
    submitted_name character varying,
    homepage_url character varying,
    jurisdiction_type character varying,
    state_iso character varying,
    municipality character varying,
    county_fips character varying,
    county_name character varying,
    lat double precision,
    lng double precision,
    defunct_year character varying,
    airtable_uid character varying NOT NULL,
    count_data_sources bigint,
    agency_type character varying,
    multi_agency boolean,
    zip_code character varying,
    data_sources character varying,
    no_web_presence boolean,
    airtable_agency_last_modified timestamp with time zone,
    data_sources_last_updated date,
    approved boolean,
    rejection_reason character varying,
    last_approval_editor character varying,
    submitter_contact character varying,
    agency_created timestamp with time zone,
    county_airtable_uid character varying
);

CREATE TABLE if not exists agency_source_link (
    link_id bigint NOT NULL,
    airtable_uid character varying NOT NULL,
    agency_described_linked_uid character varying NOT NULL
);

CREATE TABLE if not exists counties (
    fips character varying NOT NULL,
    name text,
    name_ascii text,
    state_iso text,
    lat double precision,
    lng double precision,
    population bigint,
    agencies text,
    airtable_uid text,
    airtable_county_last_modified text,
    airtable_county_created text
);

CREATE TABLE if not exists data_requests (
    request_id bigint NOT NULL,
    submission_notes text,
    request_status text,
    submitter_contact_info text,
    agency_described_submitted text,
    record_type text,
    archive_reason text,
    date_created timestamp without time zone NOT NULL,
    status_last_changed timestamp without time zone
);

CREATE TABLE if not exists data_sources (
    name character varying NOT NULL,
    submitted_name character varying,
    description character varying,
    record_type character varying,
    source_url character varying,
    agency_supplied boolean,
    supplying_entity character varying,
    agency_originated boolean,
    agency_aggregation character varying,
    coverage_start date,
    coverage_end date,
    source_last_updated date,
    detail_level character varying,
    number_of_records_available bigint,
    size character varying,
    access_type character varying,
    record_download_option_provided boolean,
    data_portal_type character varying,
    record_format character varying,
    update_frequency character varying,
    update_method character varying,
    tags character varying,
    readme_url character varying,
    originating_entity character varying,
    retention_schedule character varying,
    airtable_uid character varying NOT NULL,
    scraper_url character varying,
    data_source_created timestamp with time zone,
    airtable_source_last_modified timestamp with time zone,
    url_broken boolean,
    submission_notes character varying,
    rejection_note character varying,
    last_approval_editor character varying,
    submitter_contact_info character varying,
    agency_described_submitted character varying,
    agency_described_not_in_database character varying,
    approved boolean,
    record_type_other character varying,
    data_portal_type_other character varying,
    private_access_instructions character varying,
    records_not_online boolean,
    data_source_request character varying,
    url_button character varying,
    tags_other character varying,
    broken_source_url_as_of date,
    last_cached date,
    access_notes text,
    url_status text,
    approval_status text
);

CREATE TABLE if not exists quick_search_query_logs (
    id serial primary key,
    search character varying,
    location character varying,
    result_count bigint,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    datetime_of_request timestamp with time zone,
    results jsonb
);

CREATE TABLE if not exists state_names (
    id bigint NOT NULL,
    state_iso text NOT NULL,
    state_name text
);

CREATE TABLE if not exists users (
    id serial primary key,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    email text NOT NULL,
    password_digest text,
    api_key character varying
);

CREATE TABLE if not exists reset_tokens (
    id serial primary key,
    email text NOT NULL,
    token text varying NOT NULL,
    create_date timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists volunteers (
    discord text,
    email text,
    name text NOT NULL,
    help_topics text,
    status text,
    geographic_interest text,
    submission_notes text,
    internal_notes text,
    last_contacted timestamp without time zone,
    github text,
    created_by text,
    created timestamp without time zone NOT NULL
);

INSERT INTO agency_source_link (link_id, airtable_uid, agency_described_linked_uid) VALUES (1, 'rec00T2YLS2jU7Tbn', 'recv9fMNEQTbVarj2');
INSERT INTO agency_source_link (link_id, airtable_uid, agency_described_linked_uid) VALUES (2, 'rec8zJuEOvhAZCfAD', 'recxUlLdt3Wwov6P1');
INSERT INTO agency_source_link (link_id, airtable_uid, agency_described_linked_uid) VALUES (3, 'recUGIoPQbJ6laBmr', 'recv9fMNEQTbVarj2');
INSERT INTO agency_source_link (link_id, airtable_uid, agency_described_linked_uid) VALUES (4, 'rec8gO2K86yk9mQIU', 'recRvBpZqXM8mjddz');
INSERT INTO state_names VALUES (1, 'IL', 'Illinois');
INSERT INTO state_names VALUES (2, 'PA', 'Pennsylvania');
INSERT INTO users (id, email, password_digest) VALUES (1, "test", "test");
INSERT INTO reset_tokens (id, email, token) VALUES (1, "test", "test");
