--
-- PostgreSQL database dump
--

-- Dumped from database version 15.8
-- Dumped by pg_dump version 15.10 (Debian 15.10-1.pgdg120+1)

-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET idle_in_transaction_session_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SELECT pg_catalog.set_config('search_path', '', false);
-- SET check_function_bodies = false;
-- SET xmloption = content;
-- SET client_min_messages = warning;
-- SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: access_permission; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.access_permission AS ENUM (
    'READ',
    'WRITE',
    'NONE'
);


--
-- Name: access_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.access_type AS ENUM (
    'Download',
    'Webpage',
    'API'
);


--
-- Name: account_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.account_type AS ENUM (
    'github'
);


--
-- Name: agency_aggregation; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.agency_aggregation AS ENUM (
    'county',
    'local',
    'state',
    'federal'
);


--
-- Name: approval_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.approval_status AS ENUM (
    'approved',
    'rejected',
    'pending',
    'needs identification'
);


--
-- Name: detail_level; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.detail_level AS ENUM (
    'Individual record',
    'Aggregated records',
    'Summarized totals'
);


--
-- Name: entity_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.entity_type AS ENUM (
    'Data Request',
    'Data Source'
);


--
-- Name: event_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.event_type AS ENUM (
    'Request Ready to Start',
    'Request Complete',
    'Data Source Approved'
);


--
-- Name: jurisdiction_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.jurisdiction_type AS ENUM (
    'school',
    'county',
    'local',
    'port',
    'tribal',
    'transit',
    'state',
    'federal'
);


--
-- Name: location_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.location_type AS ENUM (
    'State',
    'County',
    'Locality'
);


--
-- Name: record_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.record_type AS ENUM (
    'Dispatch Recordings',
    'Arrest Records',
    'Citations',
    'Incarceration Records',
    'Booking Reports',
    'Budgets & Finances',
    'Misc Police Activity',
    'Geographic',
    'Crime Maps & Reports',
    'Other',
    'Annual & Monthly Reports',
    'Resources',
    'Dispatch Logs',
    'Sex Offender Registry',
    'Officer Involved Shootings',
    'Daily Activity Logs',
    'Crime Statistics',
    'Records Request Info',
    'Policies & Contracts',
    'Stops',
    'Media Bulletins',
    'Training & Hiring Info',
    'Personnel Records',
    'Contact Info & Agency Meta',
    'Incident Reports',
    'Calls for Service',
    'Accident Reports',
    'Use of Force Reports',
    'Complaints & Misconduct',
    'Vehicle Pursuits',
    'Court Cases',
    'Surveys',
    'Field Contacts',
    'Wanted Persons',
    'List of Data Sources',
    'Car GPS'
);


--
-- Name: relation_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.relation_role AS ENUM (
    'STANDARD',
    'OWNER',
    'ADMIN'
);


--
-- Name: request_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.request_status AS ENUM (
    'Intake',
    'Active',
    'Complete',
    'Request withdrawn',
    'Waiting for scraper',
    'Archived',
    'Ready to start',
    'Waiting for FOIA',
    'Waiting for requestor'
);


--
-- Name: TYPE request_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TYPE public.request_status IS '
Represents the different stages or statuses a request can have in the system:

- ''Intake'': The initial phase where the request is being gathered or evaluated.
- ''Active'': The request is currently being processed or worked on.
- ''Complete'': The request has been successfully completed and fulfilled.
- ''Request withdrawn'': The request has been withdrawn or canceled by the requester.
- ''Waiting for scraper'': The request is on hold, awaiting data collection by a web scraper.
- ''Archived'': The request has been archived, likely for long-term storage or future reference.
- ''Waiting for requestor'': The request is on hold, awaiting further information or action from the requester.
- ''Ready to Start'': The request is ready to be worked on.
- ''Waiting for FOIA'': The request is on hold, awaiting the results of a Freedom of Information Act request.
';


--
-- Name: request_urgency_level; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.request_urgency_level AS ENUM (
    'urgent',
    'somewhat_urgent',
    'not_urgent',
    'long_term',
    'indefinite_unknown'
);


--
-- Name: TYPE request_urgency_level; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TYPE public.request_urgency_level IS '
Represents the urgency of the given request:

- ''urgent'': Less than a week.
- ''somewhat_urgent'': Less than a month.
- ''not_urgent'': A few months.
- ''Long-term'': A year or more.
- ''indefinite_unknown'': The request is indefinite, or its urgency level is not known
';


--
-- Name: retention_schedule; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.retention_schedule AS ENUM (
    '< 1 day',
    '1 day',
    '< 1 week',
    '1 week',
    '1 month',
    '< 1 year',
    '1-10 years',
    '> 10 years',
    'Future only'
);


--
-- Name: search_result; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.search_result AS ENUM (
    'found_results',
    'no_results_found'
);


--
-- Name: search_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.search_status AS ENUM (
    'pending',
    'completed',
    'error',
    'no_results'
);


--
-- Name: update_method; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.update_method AS ENUM (
    'Insert',
    'No updates',
    'Overwrite'
);


--
-- Name: url_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.url_status AS ENUM (
    'ok',
    'none found',
    'broken',
    'available'
);


--
-- Name: generate_api_key(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.generate_api_key() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN gen_random_uuid();
END;
$$;


--
-- Name: insert_county_location(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.insert_county_location() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Insert a new location of type 'County' when a new county is added
    INSERT INTO locations (type, state_id, county_id)
    VALUES ('County', NEW.state_id, NEW.id);
    RETURN NEW;
END;
$$;


--
-- Name: insert_locality_location(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.insert_locality_location() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_state_id BIGINT;
BEGIN
    -- Get the state_id from the associated county
    SELECT c.state_id INTO v_state_id
    FROM counties c
    WHERE c.id = NEW.county_id;

    -- Insert a new location of type 'Locality' when a new locality is added
    INSERT INTO locations (type, state_id, county_id, locality_id)
    VALUES ('Locality', v_state_id, NEW.county_id, NEW.id);

    RETURN NEW;
END;
$$;


--
-- Name: insert_new_archive_info(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.insert_new_archive_info() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   INSERT INTO data_sources_archive_info (data_source_id)
   VALUES (NEW.id);
   RETURN NEW;
END
$$;


--
-- Name: insert_state_location(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.insert_state_location() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Insert a new location of type 'State' when a new state is added
    INSERT INTO locations (type, state_id)
    VALUES ('State', NEW.id);
    RETURN NEW;
END;
$$;


--
-- Name: maintain_recent_searches_row_limit(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.maintain_recent_searches_row_limit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if there are more than 50 rows with the same user_id
    IF (SELECT COUNT(*) FROM RECENT_SEARCHES WHERE user_id = NEW.user_id) >= 50 THEN
        -- Delete the oldest row for that b_id
        DELETE FROM RECENT_SEARCHES
        WHERE id = (
            SELECT id FROM RECENT_SEARCHES
            WHERE user_id = NEW.user_id
            ORDER BY created_at ASC
            LIMIT 1
        );
    END IF;

    -- Now the new row can be inserted as normal
    RETURN NEW;
END;
$$;


--
-- Name: FUNCTION maintain_recent_searches_row_limit(); Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON FUNCTION public.maintain_recent_searches_row_limit() IS 'Removes least recent search for a user_id if there are 50 or more rows with the same user_id';


--
-- Name: refresh_distinct_source_urls(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.refresh_distinct_source_urls()
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW distinct_source_urls;
END;
$$;


--
-- Name: refresh_typeahead_agencies(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.refresh_typeahead_agencies()
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW typeahead_agencies;
END;
$$;


--
-- Name: refresh_typeahead_locations(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.refresh_typeahead_locations()
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW typeahead_locations;
END;
$$;


--
-- Name: set_agency_name(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_agency_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.submitted_name IS NOT NULL THEN
        IF NEW.state_iso IS NOT NULL THEN
            NEW.name := NEW.submitted_name || ' - ' || NEW.state_iso;
        ELSE
            NEW.name := NEW.submitted_name;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: FUNCTION set_agency_name(); Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON FUNCTION public.set_agency_name() IS 'Updates `name` based on contents of `submitted_name` and `state_iso`';


--
-- Name: set_source_name(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_source_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.name IS NULL THEN
        NEW.name := NEW.submitted_name;
    END IF;
    RETURN NEW;
END
$$;


--
-- Name: update_airtable_agency_last_modified_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_airtable_agency_last_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.AIRTABLE_AGENCY_LAST_MODIFIED = current_timestamp;
   RETURN NEW;
END;
$$;


--
-- Name: update_approval_status_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_approval_status_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.approval_status IS DISTINCT FROM OLD.approval_status THEN
        NEW.approval_status_updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END
$$;


--
-- Name: update_broken_source_url_as_of(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_broken_source_url_as_of() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.url_status = 'broken' THEN
        NEW.broken_source_url_as_of = NOW();
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: update_data_source_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_data_source_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.updated_at = current_timestamp;
   RETURN NEW;
END;
$$;


--
-- Name: update_executed_datetime(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_executed_datetime() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update the executed_datetime when a result is inserted
    UPDATE search_queue
    SET executed_datetime = NOW()
    WHERE search_id = NEW.search_id AND executed_datetime IS NULL;

    RETURN NEW;
END;
$$;


--
-- Name: update_search_status(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_search_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Only update to 'completed' when a result is inserted
    UPDATE search_queue
    SET status = 'completed'
    WHERE search_id = NEW.search_id AND status <> 'completed';
    RETURN NEW;
END;
$$;


--
-- Name: update_status_change_date(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_status_change_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.Date_status_last_changed = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agencies (
    name character varying NOT NULL,
    submitted_name character varying NOT NULL,
    homepage_url character varying,
    jurisdiction_type public.jurisdiction_type NOT NULL,
    state_iso character varying,
    municipality character varying,
    county_fips character varying,
    county_name character varying,
    lat double precision,
    lng double precision,
    defunct_year character varying,
    airtable_uid character varying,
    agency_type character varying,
    multi_agency boolean DEFAULT false NOT NULL,
    zip_code character varying,
    no_web_presence boolean DEFAULT false NOT NULL,
    airtable_agency_last_modified timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    approved boolean DEFAULT false NOT NULL,
    rejection_reason character varying,
    last_approval_editor character varying,
    submitter_contact character varying,
    agency_created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    county_airtable_uid character varying,
    location_id bigint,
    id integer NOT NULL
);


--
-- Name: TABLE agencies; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.agencies IS 'Contains information about various agencies, including their jurisdiction, location, and administrative details.';


--
-- Name: COLUMN agencies.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.name IS 'The official name of the agency.';


--
-- Name: COLUMN agencies.submitted_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.submitted_name IS 'The name of the agency as submitted by the user.';


--
-- Name: COLUMN agencies.homepage_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.homepage_url IS 'The URL of the agency''s homepage, if available.';


--
-- Name: COLUMN agencies.jurisdiction_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.jurisdiction_type IS 'The type of jurisdiction the agency operates under (e.g., state, county, municipal).';


--
-- Name: COLUMN agencies.state_iso; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.state_iso IS 'The ISO code for the state where the agency is located.';


--
-- Name: COLUMN agencies.municipality; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.municipality IS 'The name of the municipality where the agency is located.';


--
-- Name: COLUMN agencies.county_fips; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.county_fips IS 'The FIPS code of the county where the agency is located.';


--
-- Name: COLUMN agencies.county_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.county_name IS 'The name of the county where the agency is located.';


--
-- Name: COLUMN agencies.lat; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.lat IS 'The latitude coordinate of the agency''s location.';


--
-- Name: COLUMN agencies.lng; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.lng IS 'The longitude coordinate of the agency''s location.';


--
-- Name: COLUMN agencies.defunct_year; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.defunct_year IS 'The year the agency was defunct, if applicable.';


--
-- Name: COLUMN agencies.airtable_uid; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.airtable_uid IS 'The unique identifier for the agency in Airtable.';


--
-- Name: COLUMN agencies.agency_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.agency_type IS 'The type or classification of the agency.';


--
-- Name: COLUMN agencies.multi_agency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.multi_agency IS 'Indicates whether the agency represents multiple sub-agencies.';


--
-- Name: COLUMN agencies.zip_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.zip_code IS 'The ZIP code for the agency''s location.';


--
-- Name: COLUMN agencies.no_web_presence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.no_web_presence IS 'Indicates whether the agency has no web presence.';


--
-- Name: COLUMN agencies.airtable_agency_last_modified; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.airtable_agency_last_modified IS 'The timestamp of the last modification in Airtable for the agency.';


--
-- Name: COLUMN agencies.approved; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.approved IS 'Indicates whether the agency submission has been approved.';


--
-- Name: COLUMN agencies.rejection_reason; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.rejection_reason IS 'The reason for rejecting the agency submission, if applicable.';


--
-- Name: COLUMN agencies.last_approval_editor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.last_approval_editor IS 'The identifier of the last editor who approved the agency.';


--
-- Name: COLUMN agencies.submitter_contact; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.submitter_contact IS 'The contact information for the person who submitted the agency.';


--
-- Name: COLUMN agencies.agency_created; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.agency_created IS 'The timestamp when the agency record was created.';


--
-- Name: COLUMN agencies.county_airtable_uid; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.county_airtable_uid IS 'The unique identifier for the county in Airtable.';


--
-- Name: COLUMN agencies.location_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.location_id IS 'The identifier for the location associated with the agency.';


--
-- Name: COLUMN agencies.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agencies.id IS 'The unique identifier for the agency.';


--
-- Name: counties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.counties (
    fips character varying NOT NULL,
    name text,
    name_ascii text,
    state_iso text,
    lat double precision,
    lng double precision,
    population bigint,
    agencies text,
    airtable_county_last_modified text,
    airtable_county_created text,
    id bigint NOT NULL,
    state_id integer
);


--
-- Name: TABLE counties; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.counties IS 'Stores information about counties, including geographic, population, and state association details.';


--
-- Name: COLUMN counties.fips; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.fips IS 'Federal Information Processing Standard (FIPS) code uniquely identifying the county.';


--
-- Name: COLUMN counties.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.name IS 'Full name of the county.';


--
-- Name: COLUMN counties.name_ascii; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.name_ascii IS 'ASCII-compatible version of the county name for systems with text encoding limitations.';


--
-- Name: COLUMN counties.state_iso; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.state_iso IS 'ISO code of the state the county belongs to.';


--
-- Name: COLUMN counties.lat; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.lat IS 'Latitude coordinate of the county’s approximate geographic center.';


--
-- Name: COLUMN counties.lng; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.lng IS 'Longitude coordinate of the county’s approximate geographic center.';


--
-- Name: COLUMN counties.population; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.population IS 'Population count of the county.';


--
-- Name: COLUMN counties.agencies; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.agencies IS 'Text field for storing associated agencies within the county.';


--
-- Name: COLUMN counties.airtable_county_last_modified; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.airtable_county_last_modified IS 'Timestamp for the last modification of the county record in Airtable.';


--
-- Name: COLUMN counties.airtable_county_created; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.airtable_county_created IS 'Timestamp for when the county record was created in Airtable.';


--
-- Name: COLUMN counties.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.id IS 'Primary key uniquely identifying the county in the table.';


--
-- Name: COLUMN counties.state_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.counties.state_id IS 'Foreign key referencing the associated state in the us_states table.';


--
-- Name: localities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.localities (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    county_id integer NOT NULL
);


--
-- Name: TABLE localities; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.localities IS 'Table containing information about localities including name, state, and county.';


--
-- Name: COLUMN localities.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.localities.id IS 'Primary key for the locality table.';


--
-- Name: COLUMN localities.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.localities.name IS 'Name of the locality (e.g., city, town, etc.).';


--
-- Name: COLUMN localities.county_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.localities.county_id IS 'ID of the county to which the locality belongs.';


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id bigint NOT NULL,
    type public.location_type NOT NULL,
    state_id bigint NOT NULL,
    county_id bigint,
    locality_id bigint,
    CONSTRAINT locations_check CHECK ((((type = 'State'::public.location_type) AND (county_id IS NULL) AND (locality_id IS NULL)) OR ((type = 'County'::public.location_type) AND (county_id IS NOT NULL) AND (locality_id IS NULL)) OR ((type = 'Locality'::public.location_type) AND (county_id IS NOT NULL) AND (locality_id IS NOT NULL))))
);


--
-- Name: TABLE locations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.locations IS 'Base table for storing common information for all location types.';


--
-- Name: COLUMN locations.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.locations.id IS 'Unique identifier for each location.';


--
-- Name: COLUMN locations.type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.locations.type IS 'Specifies the type of location (e.g., state, county, locality).';


--
-- Name: COLUMN locations.state_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.locations.state_id IS 'Foreign key to `us_states` table';


--
-- Name: COLUMN locations.county_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.locations.county_id IS 'Foreign key to `counties` table, if applicable';


--
-- Name: COLUMN locations.locality_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.locations.locality_id IS 'Foreign key to `localities` table, if applicable';


--
-- Name: us_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.us_states (
    state_iso text NOT NULL,
    state_name text,
    id bigint NOT NULL
);


--
-- Name: TABLE us_states; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.us_states IS 'Stores information about U.S. states, including ISO codes and state names.';


--
-- Name: COLUMN us_states.state_iso; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.us_states.state_iso IS 'ISO code uniquely identifying the state.';


--
-- Name: COLUMN us_states.state_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.us_states.state_name IS 'Full name of the state.';


--
-- Name: COLUMN us_states.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.us_states.id IS 'Primary key uniquely identifying each state record.';


--
-- Name: locations_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.locations_expanded AS
 SELECT locations.id,
    locations.type,
    us_states.state_name,
    us_states.state_iso,
    counties.name AS county_name,
    counties.fips AS county_fips,
    localities.name AS locality_name,
    localities.id AS locality_id,
    us_states.id AS state_id,
    counties.id AS county_id,
        CASE
            WHEN (locations.type = 'Locality'::public.location_type) THEN localities.name
            WHEN (locations.type = 'County'::public.location_type) THEN (counties.name)::character varying
            WHEN (locations.type = 'State'::public.location_type) THEN (us_states.state_name)::character varying
            ELSE NULL::character varying
        END AS display_name
   FROM (((public.locations
     LEFT JOIN public.us_states ON ((locations.state_id = us_states.id)))
     LEFT JOIN public.counties ON ((locations.county_id = counties.id)))
     LEFT JOIN public.localities ON ((locations.locality_id = localities.id)));


--
-- Name: VIEW locations_expanded; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.locations_expanded IS 'View containing information about locations as well as limited information from other tables connected by foreign keys.';


--
-- Name: agencies_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.agencies_expanded AS
 SELECT a.name,
    a.submitted_name,
    a.homepage_url,
    a.jurisdiction_type,
    l.state_iso,
    l.state_name,
    l.county_fips,
    l.county_name,
    a.lat,
    a.lng,
    a.defunct_year,
    a.id,
    a.agency_type,
    a.multi_agency,
    a.zip_code,
    a.no_web_presence,
    a.airtable_agency_last_modified,
    a.approved,
    a.rejection_reason,
    a.last_approval_editor,
    a.submitter_contact,
    a.agency_created,
    l.locality_name
   FROM (public.agencies a
     LEFT JOIN public.locations_expanded l ON ((a.location_id = l.id)));


--
-- Name: VIEW agencies_expanded; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.agencies_expanded IS 'View containing information about agencies as well as limited information from other tables connected by foreign keys.';


--
-- Name: agencies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agencies ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.agencies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: link_agencies_data_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_agencies_data_sources (
    id bigint NOT NULL,
    data_source_id integer NOT NULL,
    agency_id integer NOT NULL
);


--
-- Name: TABLE link_agencies_data_sources; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.link_agencies_data_sources IS 'A link table between data sources and their related agencies.';


--
-- Name: agency_source_link_agency_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_agencies_data_sources ALTER COLUMN agency_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.agency_source_link_agency_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agency_source_link_data_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_agencies_data_sources ALTER COLUMN data_source_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.agency_source_link_data_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agency_source_link_link_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_agencies_data_sources ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.agency_source_link_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agency_url_search_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agency_url_search_cache (
    id integer NOT NULL,
    search_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    search_result character varying(20),
    agency_id integer NOT NULL
);


--
-- Name: TABLE agency_url_search_cache; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.agency_url_search_cache IS 'Caches results from URL searches associated with agencies to reduce redundant queries.';


--
-- Name: COLUMN agency_url_search_cache.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agency_url_search_cache.id IS 'Primary key uniquely identifying the cache entry.';


--
-- Name: COLUMN agency_url_search_cache.search_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agency_url_search_cache.search_date IS 'Timestamp of when the URL search was performed.';


--
-- Name: COLUMN agency_url_search_cache.search_result; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agency_url_search_cache.search_result IS 'Outcome of the URL search, limited to allowable results: "found_results" or "no_results_found".';


--
-- Name: COLUMN agency_url_search_cache.agency_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.agency_url_search_cache.agency_id IS 'Foreign key referencing the agency associated with this search cache entry.';


--
-- Name: agency_url_search_cache_agency_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agency_url_search_cache ALTER COLUMN agency_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.agency_url_search_cache_agency_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agency_url_search_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agency_url_search_cache_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agency_url_search_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agency_url_search_cache_id_seq OWNED BY public.agency_url_search_cache.id;


--
-- Name: column_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.column_permission (
    id integer NOT NULL,
    rc_id integer NOT NULL,
    relation_role public.relation_role NOT NULL,
    access_permission public.access_permission NOT NULL
);


--
-- Name: TABLE column_permission; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.column_permission IS 'Stores the permissions for columns in relations based on role';


--
-- Name: COLUMN column_permission.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.column_permission.id IS 'Primary key, autogenerated';


--
-- Name: COLUMN column_permission.rc_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.column_permission.rc_id IS 'Foreign key referencing the RelationColumn table';


--
-- Name: COLUMN column_permission.relation_role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.column_permission.relation_role IS 'The role to which the permission applies';


--
-- Name: COLUMN column_permission.access_permission; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.column_permission.access_permission IS 'The level of access permission (READ, WRITE)';


--
-- Name: column_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.column_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: column_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.column_permission_id_seq OWNED BY public.column_permission.id;


--
-- Name: counties_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.counties ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.counties_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: data_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_requests (
    id bigint NOT NULL,
    submission_notes text,
    request_status public.request_status DEFAULT 'Intake'::public.request_status NOT NULL,
    archive_reason text,
    date_created timestamp with time zone DEFAULT now() NOT NULL,
    date_status_last_changed timestamp with time zone DEFAULT now() NOT NULL,
    sources_airtable_uid text,
    creator_user_id bigint,
    internal_notes text,
    record_types_required public.record_type[],
    pdap_response text,
    coverage_range character varying(255),
    data_requirements text,
    request_urgency public.request_urgency_level DEFAULT 'indefinite_unknown'::public.request_urgency_level,
    title text NOT NULL,
    CONSTRAINT title_limit CHECK ((length(title) <= 51))
);


--
-- Name: TABLE data_requests; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.data_requests IS 'Stores information related to data requests, including submission details, status, and related metadata.';


--
-- Name: COLUMN data_requests.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.id IS 'Primary key, automatically generated as a unique identifier.';


--
-- Name: COLUMN data_requests.submission_notes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.submission_notes IS 'Optional notes provided by the submitter during the request submission.';


--
-- Name: COLUMN data_requests.request_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.request_status IS 'The status of the request, using a custom enum type request_status, defaults to Intake.';


--
-- Name: COLUMN data_requests.archive_reason; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.archive_reason IS 'Reason for archiving the request, if applicable.';


--
-- Name: COLUMN data_requests.date_created; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.date_created IS 'The date and time when the request was created.';


--
-- Name: COLUMN data_requests.date_status_last_changed; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.date_status_last_changed IS 'The date and time when the status of the request was last changed.';


--
-- Name: COLUMN data_requests.creator_user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.creator_user_id IS 'The user id of the creator of the data request.';


--
-- Name: COLUMN data_requests.internal_notes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.internal_notes IS 'Internal notes by PDAP staff about the request.';


--
-- Name: COLUMN data_requests.record_types_required; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.record_types_required IS 'Multi-select of record types from record_types taxonomy.';


--
-- Name: COLUMN data_requests.pdap_response; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.pdap_response IS 'Public notes by PDAP about the request.';


--
-- Name: COLUMN data_requests.coverage_range; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.coverage_range IS 'The date range covered by the request, if applicable.';


--
-- Name: COLUMN data_requests.data_requirements; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests.data_requirements IS 'Detailed requirements for the data being requested.';


--
-- Name: data_requests_github_issue_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_requests_github_issue_info (
    id integer NOT NULL,
    data_request_id integer NOT NULL,
    github_issue_url text NOT NULL,
    github_issue_number integer NOT NULL
);


--
-- Name: TABLE data_requests_github_issue_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.data_requests_github_issue_info IS 'Stores information linking data requests to their corresponding GitHub issues.';


--
-- Name: COLUMN data_requests_github_issue_info.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests_github_issue_info.id IS 'Primary key uniquely identifying the GitHub issue information entry.';


--
-- Name: COLUMN data_requests_github_issue_info.data_request_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests_github_issue_info.data_request_id IS 'Foreign key referencing the associated data request.';


--
-- Name: COLUMN data_requests_github_issue_info.github_issue_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests_github_issue_info.github_issue_url IS 'URL of the corresponding GitHub issue.';


--
-- Name: COLUMN data_requests_github_issue_info.github_issue_number; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_requests_github_issue_info.github_issue_number IS 'Unique identifier (number) of the GitHub issue.';


--
-- Name: data_requests_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.data_requests_expanded AS
 SELECT dr.id,
    dr.title,
    dr.submission_notes,
    dr.request_status,
    dr.archive_reason,
    dr.date_created,
    dr.date_status_last_changed,
    dr.creator_user_id,
    dr.internal_notes,
    dr.record_types_required,
    dr.pdap_response,
    dr.coverage_range,
    dr.data_requirements,
    dr.request_urgency,
    drgi.github_issue_url,
    drgi.github_issue_number
   FROM (public.data_requests dr
     LEFT JOIN public.data_requests_github_issue_info drgi ON ((dr.id = drgi.data_request_id)));


--
-- Name: data_requests_github_issue_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.data_requests_github_issue_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: data_requests_github_issue_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.data_requests_github_issue_info_id_seq OWNED BY public.data_requests_github_issue_info.id;


--
-- Name: data_requests_request_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.data_requests ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.data_requests_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: data_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_sources (
    name character varying NOT NULL,
    submitted_name character varying,
    description character varying,
    source_url character varying,
    agency_supplied boolean,
    supplying_entity character varying,
    agency_originated boolean,
    agency_aggregation public.agency_aggregation,
    coverage_start date,
    coverage_end date,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    detail_level public.detail_level,
    record_download_option_provided boolean,
    data_portal_type character varying,
    update_method public.update_method,
    readme_url character varying,
    originating_entity character varying,
    retention_schedule public.retention_schedule,
    airtable_uid character varying,
    scraper_url character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    submission_notes character varying,
    rejection_note character varying,
    submitter_contact_info character varying,
    agency_described_submitted character varying,
    agency_described_not_in_database character varying,
    data_portal_type_other character varying,
    data_source_request character varying,
    broken_source_url_as_of timestamp with time zone,
    access_notes text,
    url_status public.url_status DEFAULT 'ok'::public.url_status NOT NULL,
    approval_status public.approval_status DEFAULT 'pending'::public.approval_status NOT NULL,
    record_type_id integer,
    access_types public.access_type[],
    tags text[],
    record_formats text[],
    id integer NOT NULL,
    approval_status_updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_approval_editor bigint
);


--
-- Name: TABLE data_sources; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.data_sources IS 'Stores information about data sources, including metadata, origin, and approval status.';


--
-- Name: COLUMN data_sources.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.name IS 'Name of the data source.';


--
-- Name: COLUMN data_sources.submitted_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.submitted_name IS 'Name of the data source submitted by the user.';


--
-- Name: COLUMN data_sources.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.description IS 'Description of the data source.';


--
-- Name: COLUMN data_sources.source_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.source_url IS 'URL where the data source can be accessed.';


--
-- Name: COLUMN data_sources.agency_supplied; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.agency_supplied IS 'Indicates if the data source is supplied directly by an agency.';


--
-- Name: COLUMN data_sources.supplying_entity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.supplying_entity IS 'Entity that supplied the data source.';


--
-- Name: COLUMN data_sources.agency_originated; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.agency_originated IS 'Indicates if the data source originated from an agency.';


--
-- Name: COLUMN data_sources.agency_aggregation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.agency_aggregation IS 'Whether this data source comes from multiple agencies.';


--
-- Name: COLUMN data_sources.coverage_start; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.coverage_start IS 'Start date of the data source’s coverage.';


--
-- Name: COLUMN data_sources.coverage_end; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.coverage_end IS 'End date of the data source’s coverage.';


--
-- Name: COLUMN data_sources.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.updated_at IS 'Timestamp of the last update to the data source record.';


--
-- Name: COLUMN data_sources.detail_level; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.detail_level IS 'Level of detail provided by the data source.';


--
-- Name: COLUMN data_sources.record_download_option_provided; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.record_download_option_provided IS 'Indicates if the data source provides an option for downloading records.';


--
-- Name: COLUMN data_sources.data_portal_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.data_portal_type IS 'Type of data portal providing access to the data source.';


--
-- Name: COLUMN data_sources.update_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.update_method IS 'Method used to update the data source.';


--
-- Name: COLUMN data_sources.readme_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.readme_url IS 'URL to the README or documentation for the data source.';


--
-- Name: COLUMN data_sources.originating_entity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.originating_entity IS 'Entity where the data source originated.';


--
-- Name: COLUMN data_sources.retention_schedule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.retention_schedule IS 'Retention schedule for the data source records.';


--
-- Name: COLUMN data_sources.airtable_uid; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.airtable_uid IS 'Unique identifier for the data source in Airtable.';


--
-- Name: COLUMN data_sources.scraper_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.scraper_url IS 'URL to the scraper used for this data source, if applicable.';


--
-- Name: COLUMN data_sources.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.created_at IS 'Timestamp when the data source record was created.';


--
-- Name: COLUMN data_sources.submission_notes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.submission_notes IS 'Notes submitted during the data source submission.';


--
-- Name: COLUMN data_sources.rejection_note; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.rejection_note IS 'Reason provided for rejecting the data source.';


--
-- Name: COLUMN data_sources.submitter_contact_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.submitter_contact_info IS 'Contact information of the data source submitter.';


--
-- Name: COLUMN data_sources.agency_described_submitted; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.agency_described_submitted IS 'Agency description provided by the submitter.';


--
-- Name: COLUMN data_sources.agency_described_not_in_database; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.agency_described_not_in_database IS 'Agency description not included in the database.';


--
-- Name: COLUMN data_sources.data_portal_type_other; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.data_portal_type_other IS 'Additional description of the data portal type if "other" is selected.';


--
-- Name: COLUMN data_sources.data_source_request; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.data_source_request IS 'Information about a specific data source request.';


--
-- Name: COLUMN data_sources.broken_source_url_as_of; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.broken_source_url_as_of IS 'Timestamp indicating when the source URL was reported as broken.';


--
-- Name: COLUMN data_sources.access_notes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.access_notes IS 'Notes regarding access to the data source.';


--
-- Name: COLUMN data_sources.url_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.url_status IS 'Status of the source URL (e.g., "ok", "broken").';


--
-- Name: COLUMN data_sources.approval_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.approval_status IS 'Approval status of the data source (e.g., "pending", "approved").';


--
-- Name: COLUMN data_sources.record_type_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.record_type_id IS 'Foreign key referencing the type of record associated with the data source.';


--
-- Name: COLUMN data_sources.access_types; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.access_types IS 'Array of access types available for the data source.';


--
-- Name: COLUMN data_sources.tags; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.tags IS 'Array of tags associated with the data source.';


--
-- Name: COLUMN data_sources.record_formats; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.record_formats IS 'Array of formats in which the data source records are available.';


--
-- Name: COLUMN data_sources.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.id IS 'Primary key uniquely identifying the data source.';


--
-- Name: COLUMN data_sources.approval_status_updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.approval_status_updated_at IS 'Timestamp when the approval status was last updated.';


--
-- Name: COLUMN data_sources.last_approval_editor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources.last_approval_editor IS 'Foreign key referencing the user who last updated the approval status.';


--
-- Name: data_sources_archive_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_sources_archive_info (
    update_frequency character varying,
    last_cached timestamp without time zone,
    next_cache timestamp without time zone,
    data_source_id integer NOT NULL
);


--
-- Name: TABLE data_sources_archive_info; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.data_sources_archive_info IS 'Stores information about the archival and caching frequency of data sources.';


--
-- Name: COLUMN data_sources_archive_info.update_frequency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources_archive_info.update_frequency IS 'Frequency at which the data source is updated (e.g., daily, weekly).';


--
-- Name: COLUMN data_sources_archive_info.last_cached; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources_archive_info.last_cached IS 'Timestamp indicating when the data source was last cached.';


--
-- Name: COLUMN data_sources_archive_info.next_cache; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources_archive_info.next_cache IS 'Timestamp indicating when the next caching process is scheduled.';


--
-- Name: COLUMN data_sources_archive_info.data_source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.data_sources_archive_info.data_source_id IS 'Primary key and foreign key referencing the associated data source in the data_sources table.';


--
-- Name: data_sources_archive_info_data_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.data_sources_archive_info ALTER COLUMN data_source_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.data_sources_archive_info_data_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: record_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.record_types (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    category_id integer NOT NULL,
    description text
);


--
-- Name: TABLE record_types; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.record_types IS 'Defines specific types of records and associates them with broader categories.';


--
-- Name: COLUMN record_types.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_types.id IS 'Primary key uniquely identifying the record type.';


--
-- Name: COLUMN record_types.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_types.name IS 'Name of the record type, used as a unique identifier.';


--
-- Name: COLUMN record_types.category_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_types.category_id IS 'Foreign key referencing the category this record type belongs to.';


--
-- Name: COLUMN record_types.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_types.description IS 'Optional text providing a detailed description of the record type.';


--
-- Name: data_sources_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.data_sources_expanded AS
 SELECT ds.name,
    ds.submitted_name,
    ds.description,
    ds.source_url,
    ds.agency_supplied,
    ds.supplying_entity,
    ds.agency_originated,
    ds.agency_aggregation,
    ds.coverage_start,
    ds.coverage_end,
    ds.updated_at,
    ds.detail_level,
    ds.data_portal_type,
    ds.update_method,
    ds.readme_url,
    ds.originating_entity,
    ds.retention_schedule,
    ds.id,
    ds.scraper_url,
    ds.created_at,
    ds.submission_notes,
    ds.rejection_note,
    ds.last_approval_editor,
    ds.submitter_contact_info,
    ds.agency_described_submitted,
    ds.agency_described_not_in_database,
    ds.data_portal_type_other,
    ds.data_source_request,
    ds.broken_source_url_as_of,
    ds.access_notes,
    ds.url_status,
    ds.approval_status,
    ds.record_type_id,
    rt.name AS record_type_name,
    ds.access_types,
    ds.tags,
    ds.record_formats,
    ds.approval_status_updated_at
   FROM (public.data_sources ds
     LEFT JOIN public.record_types rt ON ((ds.record_type_id = rt.id)));


--
-- Name: data_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.data_sources ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.data_sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dependent_locations; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.dependent_locations AS
 SELECT lp.id AS parent_location_id,
    ld.id AS dependent_location_id
   FROM (public.locations lp
     JOIN public.locations ld ON (((ld.state_id = lp.state_id) AND (ld.type = 'County'::public.location_type) AND (lp.type = 'State'::public.location_type))))
UNION ALL
 SELECT lp.id AS parent_location_id,
    ld.id AS dependent_location_id
   FROM (public.locations lp
     JOIN public.locations ld ON (((ld.county_id = lp.county_id) AND (ld.type = 'Locality'::public.location_type) AND (lp.type = 'County'::public.location_type))))
UNION ALL
 SELECT lp.id AS parent_location_id,
    ld.id AS dependent_location_id
   FROM (public.locations lp
     JOIN public.locations ld ON (((ld.state_id = lp.state_id) AND (ld.type = 'Locality'::public.location_type) AND (lp.type = 'State'::public.location_type))));


--
-- Name: VIEW dependent_locations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.dependent_locations IS 'Expresses which locations are dependent locations of other locations; for example: a county is a dependent location of a state, and a locality is a dependent location of a state and county';


--
-- Name: distinct_source_urls; Type: MATERIALIZED VIEW; Schema: public; Owner: -
--

CREATE MATERIALIZED VIEW public.distinct_source_urls AS
 SELECT DISTINCT rtrim(ltrim(ltrim(ltrim((data_sources.source_url)::text, 'https://'::text), 'http://'::text), 'www.'::text), '/'::text) AS base_url,
    data_sources.source_url AS original_url,
    data_sources.rejection_note,
    data_sources.approval_status
   FROM public.data_sources
  WHERE (data_sources.source_url IS NOT NULL)
  WITH NO DATA;


--
-- Name: external_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.external_accounts (
    row_id integer NOT NULL,
    user_id integer NOT NULL,
    account_type public.account_type NOT NULL,
    account_identifier character varying(255) NOT NULL,
    linked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE external_accounts; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.external_accounts IS 'Stores information about external accounts linked to user profiles.';


--
-- Name: COLUMN external_accounts.row_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_accounts.row_id IS 'Primary key uniquely identifying the external account record.';


--
-- Name: COLUMN external_accounts.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_accounts.user_id IS 'Foreign key referencing the user to whom the external account is linked.';


--
-- Name: COLUMN external_accounts.account_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_accounts.account_type IS 'Type of the external account (e.g., GitHub, Google, LinkedIn).';


--
-- Name: COLUMN external_accounts.account_identifier; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_accounts.account_identifier IS 'Unique identifier for the external account (e.g., username, email, or account ID).';


--
-- Name: COLUMN external_accounts.linked_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_accounts.linked_at IS 'Timestamp indicating when the external account was linked to the user profile.';


--
-- Name: external_accounts_row_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.external_accounts_row_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: external_accounts_row_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.external_accounts_row_id_seq OWNED BY public.external_accounts.row_id;


--
-- Name: link_data_sources_data_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_data_sources_data_requests (
    id integer NOT NULL,
    request_id integer NOT NULL,
    data_source_id integer NOT NULL
);


--
-- Name: TABLE link_data_sources_data_requests; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.link_data_sources_data_requests IS 'A link table associating data sources with related data requests.';


--
-- Name: COLUMN link_data_sources_data_requests.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_data_sources_data_requests.id IS 'Primary key, auto-incrementing';


--
-- Name: COLUMN link_data_sources_data_requests.request_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_data_sources_data_requests.request_id IS 'Foreign key referencing data_requests';


--
-- Name: link_data_sources_data_requests_data_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_data_sources_data_requests ALTER COLUMN data_source_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.link_data_sources_data_requests_data_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: link_data_sources_data_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.link_data_sources_data_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: link_data_sources_data_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.link_data_sources_data_requests_id_seq OWNED BY public.link_data_sources_data_requests.id;


--
-- Name: link_locations_data_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_locations_data_requests (
    id bigint NOT NULL,
    location_id integer NOT NULL,
    data_request_id integer NOT NULL
);


--
-- Name: TABLE link_locations_data_requests; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.link_locations_data_requests IS 'Links locations to data requests, establishing many-to-many relationships between the two entities.';


--
-- Name: COLUMN link_locations_data_requests.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_locations_data_requests.id IS 'Primary key uniquely identifying the link between a location and a data request.';


--
-- Name: COLUMN link_locations_data_requests.location_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_locations_data_requests.location_id IS 'Foreign key referencing the location associated with the data request.';


--
-- Name: COLUMN link_locations_data_requests.data_request_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_locations_data_requests.data_request_id IS 'Foreign key referencing the data request associated with the location.';


--
-- Name: link_locations_data_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_locations_data_requests ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.link_locations_data_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: link_recent_search_record_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_recent_search_record_categories (
    id bigint NOT NULL,
    recent_search_id integer NOT NULL,
    record_category_id integer NOT NULL
);


--
-- Name: TABLE link_recent_search_record_categories; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.link_recent_search_record_categories IS 'Link table between recent searches and record categories searched for in that search';


--
-- Name: link_recent_search_record_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_recent_search_record_categories ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.link_recent_search_record_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: link_user_followed_location; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_user_followed_location (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    location_id integer NOT NULL
);


--
-- Name: TABLE link_user_followed_location; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.link_user_followed_location IS 'A link table between users and their followed locations.';


--
-- Name: COLUMN link_user_followed_location.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_user_followed_location.id IS 'Primary key, auto-incrementing';


--
-- Name: COLUMN link_user_followed_location.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_user_followed_location.user_id IS 'Foreign key referencing users';


--
-- Name: COLUMN link_user_followed_location.location_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.link_user_followed_location.location_id IS 'Foreign key referencing locations';


--
-- Name: link_user_followed_location_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.link_user_followed_location ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.link_user_followed_location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: localities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.localities ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.localities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.locations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.locations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: num_agencies_per_data_source; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.num_agencies_per_data_source AS
 SELECT count(l.agency_id) AS agency_count,
    l.data_source_id
   FROM public.link_agencies_data_sources l
  GROUP BY l.data_source_id;


--
-- Name: VIEW num_agencies_per_data_source; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.num_agencies_per_data_source IS 'View containing the number of agencies associated with each data source';


--
-- Name: num_data_sources_per_agency; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.num_data_sources_per_agency AS
 SELECT count(l.data_source_id) AS data_source_count,
    l.agency_id
   FROM public.link_agencies_data_sources l
  GROUP BY l.agency_id;


--
-- Name: VIEW num_data_sources_per_agency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.num_data_sources_per_agency IS 'View containing the number of data sources associated with each agency';


--
-- Name: pending_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pending_users (
    id bigint NOT NULL,
    email text NOT NULL,
    password_digest text NOT NULL,
    validation_token text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE pending_users; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.pending_users IS 'Table for storing pending users';


--
-- Name: COLUMN pending_users.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pending_users.id IS 'Primary key, auto-incrementing';


--
-- Name: COLUMN pending_users.email; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pending_users.email IS 'Email address';


--
-- Name: COLUMN pending_users.password_digest; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pending_users.password_digest IS 'Password hash';


--
-- Name: COLUMN pending_users.validation_token; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pending_users.validation_token IS 'Validation token to use when verifying email';


--
-- Name: COLUMN pending_users.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pending_users.created_at IS 'Timestamp of creation';


--
-- Name: pending_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.pending_users ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.pending_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permissions (
    permission_id integer NOT NULL,
    permission_name character varying(255) NOT NULL,
    description text
);


--
-- Name: TABLE permissions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.permissions IS 'This table stores the permissions available in the system, defining various access roles and their descriptions.';


--
-- Name: COLUMN permissions.permission_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.permissions.permission_id IS 'Primary key of the Permissions table, automatically generated';


--
-- Name: COLUMN permissions.permission_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.permissions.permission_name IS 'Unique name of the permission role';


--
-- Name: COLUMN permissions.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.permissions.description IS 'Detailed description of what the permission allows';


--
-- Name: permissions_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.permissions_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissions_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.permissions_permission_id_seq OWNED BY public.permissions.permission_id;


--
-- Name: qualifying_notifications; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.qualifying_notifications AS
 WITH cutoff_point AS (
         SELECT (date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone) - '1 mon'::interval) AS date_range_min,
            date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone) AS date_range_max
        )
 SELECT
        CASE
            WHEN (dr.request_status = 'Ready to start'::public.request_status) THEN 'Request Ready to Start'::public.event_type
            WHEN (dr.request_status = 'Complete'::public.request_status) THEN 'Request Complete'::public.event_type
            ELSE NULL::public.event_type
        END AS event_type,
    dr.id AS entity_id,
    'Data Request'::public.entity_type AS entity_type,
    dr.title AS entity_name,
    lnk_dr.location_id,
    dr.date_status_last_changed AS event_timestamp
   FROM cutoff_point cp,
    (public.data_requests dr
     JOIN public.link_locations_data_requests lnk_dr ON ((lnk_dr.data_request_id = dr.id)))
  WHERE ((dr.date_status_last_changed > cp.date_range_min) AND (dr.date_status_last_changed < cp.date_range_max) AND ((dr.request_status = 'Ready to start'::public.request_status) OR (dr.request_status = 'Complete'::public.request_status)))
UNION ALL
 SELECT 'Data Source Approved'::public.event_type AS event_type,
    ds.id AS entity_id,
    'Data Source'::public.entity_type AS entity_type,
    ds.name AS entity_name,
    a.location_id,
    ds.approval_status_updated_at AS event_timestamp
   FROM cutoff_point cp,
    ((public.data_sources ds
     JOIN public.link_agencies_data_sources lnk ON ((lnk.data_source_id = ds.id)))
     JOIN public.agencies a ON ((lnk.agency_id = a.id)))
  WHERE ((ds.approval_status_updated_at > cp.date_range_min) AND (ds.approval_status_updated_at < cp.date_range_max) AND (ds.approval_status = 'approved'::public.approval_status));


--
-- Name: VIEW qualifying_notifications; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.qualifying_notifications IS 'List of data requests and data sources that qualify for notifications';


--
-- Name: recent_searches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recent_searches (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    location_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: TABLE recent_searches; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.recent_searches IS 'Table logging last 50 searches for each user';


--
-- Name: recent_searches_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.recent_searches_expanded AS
SELECT
    NULL::bigint AS id,
    NULL::integer AS user_id,
    NULL::integer AS location_id,
    NULL::text AS county_name,
    NULL::character varying(255) AS locality_name,
    NULL::public.location_type AS location_type,
    NULL::character varying[] AS record_categories,
    NULL::text AS state_name;


--
-- Name: VIEW recent_searches_expanded; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.recent_searches_expanded IS 'Expanded view of recent searches, including location and record category information';


--
-- Name: recent_searches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.recent_searches ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.recent_searches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: record_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.record_categories (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text
);


--
-- Name: TABLE record_categories; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.record_categories IS 'Stores categories used to classify records for organizational and descriptive purposes.';


--
-- Name: COLUMN record_categories.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_categories.id IS 'Primary key uniquely identifying the record category.';


--
-- Name: COLUMN record_categories.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_categories.name IS 'Name of the record category, used as a unique identifier.';


--
-- Name: COLUMN record_categories.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.record_categories.description IS 'Optional text providing a detailed description of the record category.';


--
-- Name: record_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.record_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: record_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.record_categories_id_seq OWNED BY public.record_categories.id;


--
-- Name: record_types_expanded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.record_types_expanded AS
 SELECT rt.id AS record_type_id,
    rt.name AS record_type_name,
    rc.id AS record_category_id,
    rc.name AS record_category_name
   FROM (public.record_types rt
     JOIN public.record_categories rc ON ((rt.category_id = rc.id)));


--
-- Name: record_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.record_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: record_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.record_types_id_seq OWNED BY public.record_types.id;


--
-- Name: relation_column; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.relation_column (
    id integer NOT NULL,
    relation text NOT NULL,
    associated_column text NOT NULL
);


--
-- Name: TABLE relation_column; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.relation_column IS 'Stores the relation and corresponding columns';


--
-- Name: COLUMN relation_column.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.relation_column.id IS 'Primary key, autogenerated';


--
-- Name: COLUMN relation_column.relation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.relation_column.relation IS 'The relation (table or view) name';


--
-- Name: COLUMN relation_column.associated_column; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.relation_column.associated_column IS 'The column within the specified relation';


--
-- Name: relation_column_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.relation_column_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: relation_column_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.relation_column_id_seq OWNED BY public.relation_column.id;


--
-- Name: relation_column_permission_view; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.relation_column_permission_view AS
 SELECT rc.relation,
    rc.associated_column,
    cp.relation_role,
    cp.access_permission
   FROM (public.relation_column rc
     LEFT JOIN public.column_permission cp ON ((cp.rc_id = rc.id)));


--
-- Name: VIEW relation_column_permission_view; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.relation_column_permission_view IS 'A combined view of the non-id columns in `relation_column` and `column_permission` tables';


--
-- Name: reset_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reset_tokens (
    id integer NOT NULL,
    token text,
    create_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id bigint
);


--
-- Name: TABLE reset_tokens; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.reset_tokens IS 'Stores password reset tokens for users, including creation timestamp and associated user.';


--
-- Name: COLUMN reset_tokens.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reset_tokens.id IS 'Primary key uniquely identifying the reset token record.';


--
-- Name: COLUMN reset_tokens.token; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reset_tokens.token IS 'Unique token generated for resetting a user’s password.';


--
-- Name: COLUMN reset_tokens.create_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reset_tokens.create_date IS 'Timestamp indicating when the reset token was created.';


--
-- Name: COLUMN reset_tokens.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reset_tokens.user_id IS 'Foreign key referencing the user associated with the reset token.';


--
-- Name: reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reset_tokens_id_seq OWNED BY public.reset_tokens.id;


--
-- Name: search_batch_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_batch_info (
    batch_id integer NOT NULL,
    short_name character varying(255) NOT NULL,
    description text,
    initiated_datetime timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: search_batch_info_batch_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.search_batch_info_batch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: search_batch_info_batch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.search_batch_info_batch_id_seq OWNED BY public.search_batch_info.batch_id;


--
-- Name: search_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_links (
    link_id integer NOT NULL,
    search_id integer NOT NULL,
    link_description text,
    linked_table_name character varying[] NOT NULL,
    linked_column_name character varying[] NOT NULL,
    linked_column_id integer NOT NULL
);


--
-- Name: search_links_link_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.search_links_link_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: search_links_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.search_links_link_id_seq OWNED BY public.search_links.link_id;


--
-- Name: search_queue; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_queue (
    search_id integer NOT NULL,
    batch_id integer NOT NULL,
    search_query text NOT NULL,
    executed_datetime timestamp without time zone,
    status public.search_status DEFAULT 'pending'::public.search_status
);


--
-- Name: search_queue_search_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.search_queue_search_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: search_queue_search_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.search_queue_search_id_seq OWNED BY public.search_queue.search_id;


--
-- Name: search_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_results (
    result_id integer NOT NULL,
    search_id integer NOT NULL,
    url character varying(2048) NOT NULL,
    title character varying(512),
    snippet text
);


--
-- Name: search_results_result_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.search_results_result_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: search_results_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.search_results_result_id_seq OWNED BY public.search_results.result_id;


--
-- Name: test_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_table (
    id bigint NOT NULL,
    pet_name character varying(255),
    species character varying(255)
);


--
-- Name: TABLE test_table; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.test_table IS 'A test table for testing various database queries.';


--
-- Name: test_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.test_table ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.test_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: typeahead_agencies; Type: MATERIALIZED VIEW; Schema: public; Owner: -
--

CREATE MATERIALIZED VIEW public.typeahead_agencies AS
 SELECT a.id,
    a.name,
    a.jurisdiction_type,
    l.state_iso,
    l.locality_name AS municipality,
    l.county_name
   FROM (public.agencies a
     LEFT JOIN public.locations_expanded l ON ((a.location_id = l.id)))
  WITH NO DATA;


--
-- Name: typeahead_locations; Type: MATERIALIZED VIEW; Schema: public; Owner: -
--

CREATE MATERIALIZED VIEW public.typeahead_locations AS
 SELECT locations_expanded.id AS location_id,
        CASE
            WHEN (locations_expanded.type = 'Locality'::public.location_type) THEN locations_expanded.locality_name
            WHEN (locations_expanded.type = 'County'::public.location_type) THEN (locations_expanded.county_name)::character varying
            WHEN (locations_expanded.type = 'State'::public.location_type) THEN (locations_expanded.state_name)::character varying
            ELSE NULL::character varying
        END AS display_name,
    locations_expanded.type,
    locations_expanded.state_name,
    locations_expanded.county_name,
    locations_expanded.locality_name
   FROM public.locations_expanded
  WITH NO DATA;


--
-- Name: us_states_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.us_states ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.us_states_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    email text NOT NULL,
    password_digest text,
    api_key character varying,
    role text
);


--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.users IS 'Stores information about users, including authentication details, roles, and timestamps for account creation and updates.';


--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.id IS 'Primary key uniquely identifying the user.';


--
-- Name: COLUMN users.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.created_at IS 'Timestamp indicating when the user account was created.';


--
-- Name: COLUMN users.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.updated_at IS 'Timestamp indicating the last time the user account was updated.';


--
-- Name: COLUMN users.email; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.email IS 'Email address of the user, used as a unique identifier for login.';


--
-- Name: COLUMN users.password_digest; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.password_digest IS 'Hashed password for secure authentication.';


--
-- Name: COLUMN users.api_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.api_key IS 'API key assigned to the user for programmatic access.';


--
-- Name: COLUMN users.role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.role IS 'Role assigned to the user, defining permissions and access levels (e.g., admin, standard user).';


--
-- Name: user_external_accounts; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.user_external_accounts AS
 SELECT u.id,
    u.email,
    ea.account_type,
    ea.account_identifier,
    ea.linked_at
   FROM (public.users u
     LEFT JOIN public.external_accounts ea ON ((u.id = ea.user_id)));


--
-- Name: user_notification_queue; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_notification_queue (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    email text NOT NULL,
    entity_id integer NOT NULL,
    entity_type public.entity_type NOT NULL,
    entity_name text NOT NULL,
    event_type public.event_type NOT NULL,
    event_timestamp timestamp with time zone NOT NULL,
    sent_at timestamp with time zone
);


--
-- Name: TABLE user_notification_queue; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.user_notification_queue IS 'Queue for user notifications for past month.';


--
-- Name: user_notification_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.user_notification_queue ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.user_notification_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_pending_notifications; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.user_pending_notifications AS
 SELECT DISTINCT q.event_type,
    q.entity_id,
    q.entity_type,
    q.entity_name,
    q.location_id,
    q.event_timestamp,
    l.user_id,
    u.email
   FROM (((public.qualifying_notifications q
     JOIN public.dependent_locations d ON ((d.dependent_location_id = q.location_id)))
     JOIN public.link_user_followed_location l ON (((l.location_id = q.location_id) OR (l.location_id = d.parent_location_id))))
     JOIN public.users u ON ((u.id = l.user_id)));


--
-- Name: VIEW user_pending_notifications; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.user_pending_notifications IS 'View of all pending notifications for individual users.';


--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_permissions (
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: TABLE user_permissions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.user_permissions IS 'This table links users to their assigned permissions, indicating which permissions each user has.';


--
-- Name: COLUMN user_permissions.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_permissions.user_id IS 'Foreign key referencing the Users table, indicating the user who has the permission.';


--
-- Name: COLUMN user_permissions.permission_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_permissions.permission_id IS 'Foreign key referencing the Permissions table, indicating the permission assigned to the user.';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: zip_codes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.zip_codes (
    zip_code text,
    lat numeric,
    lng numeric
);


--
-- Name: TABLE zip_codes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.zip_codes IS 'Stores information about ZIP codes, including their geographic coordinates.';


--
-- Name: COLUMN zip_codes.zip_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.zip_codes.zip_code IS 'ZIP code representing a specific postal area.';


--
-- Name: COLUMN zip_codes.lat; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.zip_codes.lat IS 'Latitude coordinate of the geographic center of the ZIP code area.';


--
-- Name: COLUMN zip_codes.lng; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.zip_codes.lng IS 'Longitude coordinate of the geographic center of the ZIP code area.';


--
-- Name: agency_url_search_cache id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agency_url_search_cache ALTER COLUMN id SET DEFAULT nextval('public.agency_url_search_cache_id_seq'::regclass);


--
-- Name: column_permission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.column_permission ALTER COLUMN id SET DEFAULT nextval('public.column_permission_id_seq'::regclass);


--
-- Name: data_requests_github_issue_info id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info ALTER COLUMN id SET DEFAULT nextval('public.data_requests_github_issue_info_id_seq'::regclass);


--
-- Name: external_accounts row_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_accounts ALTER COLUMN row_id SET DEFAULT nextval('public.external_accounts_row_id_seq'::regclass);


--
-- Name: link_data_sources_data_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_data_sources_data_requests ALTER COLUMN id SET DEFAULT nextval('public.link_data_sources_data_requests_id_seq'::regclass);


--
-- Name: permissions permission_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions ALTER COLUMN permission_id SET DEFAULT nextval('public.permissions_permission_id_seq'::regclass);


--
-- Name: record_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_categories ALTER COLUMN id SET DEFAULT nextval('public.record_categories_id_seq'::regclass);


--
-- Name: record_types id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_types ALTER COLUMN id SET DEFAULT nextval('public.record_types_id_seq'::regclass);


--
-- Name: relation_column id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.relation_column ALTER COLUMN id SET DEFAULT nextval('public.relation_column_id_seq'::regclass);


--
-- Name: reset_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.reset_tokens_id_seq'::regclass);


--
-- Name: search_batch_info batch_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_batch_info ALTER COLUMN batch_id SET DEFAULT nextval('public.search_batch_info_batch_id_seq'::regclass);


--
-- Name: search_links link_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_links ALTER COLUMN link_id SET DEFAULT nextval('public.search_links_link_id_seq'::regclass);


--
-- Name: search_queue search_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_queue ALTER COLUMN search_id SET DEFAULT nextval('public.search_queue_search_id_seq'::regclass);


--
-- Name: search_results result_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_results ALTER COLUMN result_id SET DEFAULT nextval('public.search_results_result_id_seq'::regclass);


--
-- Name: agency_url_search_cache CK_ALLOWABLE_SEARCH_RESULTS; Type: CHECK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.agency_url_search_cache
    ADD CONSTRAINT "CK_ALLOWABLE_SEARCH_RESULTS" CHECK (((search_result)::text = ANY (ARRAY[('found_results'::character varying)::text, ('no_results_found'::character varying)::text]))) NOT VALID;


--
-- Name: agencies agencies_id_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agencies
    ADD CONSTRAINT agencies_id_unique UNIQUE (id);


--
-- Name: agencies agencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agencies
    ADD CONSTRAINT agencies_pkey PRIMARY KEY (id);


--
-- Name: link_agencies_data_sources agency_source_link_link_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_agencies_data_sources
    ADD CONSTRAINT agency_source_link_link_id_key UNIQUE (id);


--
-- Name: link_agencies_data_sources agency_source_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_agencies_data_sources
    ADD CONSTRAINT agency_source_link_pkey PRIMARY KEY (data_source_id, agency_id);


--
-- Name: agency_url_search_cache agency_url_search_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agency_url_search_cache
    ADD CONSTRAINT agency_url_search_cache_pkey PRIMARY KEY (id);


--
-- Name: column_permission column_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.column_permission
    ADD CONSTRAINT column_permission_pkey PRIMARY KEY (id);


--
-- Name: counties counties_fips_state_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.counties
    ADD CONSTRAINT counties_fips_state_id_key UNIQUE (fips, state_id);


--
-- Name: counties counties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.counties
    ADD CONSTRAINT counties_pkey PRIMARY KEY (id);


--
-- Name: data_requests_github_issue_info data_requests_github_issue_info_data_request_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info
    ADD CONSTRAINT data_requests_github_issue_info_data_request_id_key UNIQUE (data_request_id);


--
-- Name: data_requests_github_issue_info data_requests_github_issue_info_github_issue_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info
    ADD CONSTRAINT data_requests_github_issue_info_github_issue_number_key UNIQUE (github_issue_number);


--
-- Name: data_requests_github_issue_info data_requests_github_issue_info_github_issue_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info
    ADD CONSTRAINT data_requests_github_issue_info_github_issue_url_key UNIQUE (github_issue_url);


--
-- Name: data_requests_github_issue_info data_requests_github_issue_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info
    ADD CONSTRAINT data_requests_github_issue_info_pkey PRIMARY KEY (id);


--
-- Name: data_requests data_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests
    ADD CONSTRAINT data_requests_pkey PRIMARY KEY (id);


--
-- Name: data_sources_archive_info data_sources_archive_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources_archive_info
    ADD CONSTRAINT data_sources_archive_info_pkey PRIMARY KEY (data_source_id);


--
-- Name: data_sources data_sources_id_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_id_unique UNIQUE (id);


--
-- Name: data_sources data_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_pkey PRIMARY KEY (id);


--
-- Name: external_accounts external_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_accounts
    ADD CONSTRAINT external_accounts_pkey PRIMARY KEY (row_id);


--
-- Name: external_accounts external_accounts_user_id_account_type_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_accounts
    ADD CONSTRAINT external_accounts_user_id_account_type_key UNIQUE (user_id, account_type);


--
-- Name: link_data_sources_data_requests link_data_sources_data_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_data_sources_data_requests
    ADD CONSTRAINT link_data_sources_data_requests_pkey PRIMARY KEY (id);


--
-- Name: link_locations_data_requests link_locations_data_requests_location_id_data_request_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_locations_data_requests
    ADD CONSTRAINT link_locations_data_requests_location_id_data_request_id_key UNIQUE (location_id, data_request_id);


--
-- Name: link_locations_data_requests link_locations_data_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_locations_data_requests
    ADD CONSTRAINT link_locations_data_requests_pkey PRIMARY KEY (id);


--
-- Name: link_recent_search_record_categories link_recent_search_record_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_recent_search_record_categories
    ADD CONSTRAINT link_recent_search_record_categories_pkey PRIMARY KEY (id);


--
-- Name: link_user_followed_location link_user_followed_location_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_user_followed_location
    ADD CONSTRAINT link_user_followed_location_pkey PRIMARY KEY (id);


--
-- Name: localities localities_name_county_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localities
    ADD CONSTRAINT localities_name_county_id_key UNIQUE (name, county_id);


--
-- Name: localities localities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localities
    ADD CONSTRAINT localities_pkey PRIMARY KEY (id);


--
-- Name: locations locations_id_type_state_id_county_id_locality_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_id_type_state_id_county_id_locality_id_key UNIQUE (id, type, state_id, county_id, locality_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: pending_users pending_users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pending_users
    ADD CONSTRAINT pending_users_email_key UNIQUE (email);


--
-- Name: pending_users pending_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pending_users
    ADD CONSTRAINT pending_users_pkey PRIMARY KEY (id);


--
-- Name: pending_users pending_users_validation_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pending_users
    ADD CONSTRAINT pending_users_validation_token_key UNIQUE (validation_token);


--
-- Name: permissions permissions_permission_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_permission_name_key UNIQUE (permission_name);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (permission_id);


--
-- Name: recent_searches recent_searches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recent_searches
    ADD CONSTRAINT recent_searches_pkey PRIMARY KEY (id);


--
-- Name: record_categories record_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_categories
    ADD CONSTRAINT record_categories_name_key UNIQUE (name);


--
-- Name: record_categories record_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_categories
    ADD CONSTRAINT record_categories_pkey PRIMARY KEY (id);


--
-- Name: record_types record_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_types
    ADD CONSTRAINT record_types_name_key UNIQUE (name);


--
-- Name: record_types record_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_types
    ADD CONSTRAINT record_types_pkey PRIMARY KEY (id);


--
-- Name: relation_column relation_column_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.relation_column
    ADD CONSTRAINT relation_column_pkey PRIMARY KEY (id);


--
-- Name: reset_tokens reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reset_tokens
    ADD CONSTRAINT reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: search_batch_info search_batch_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_batch_info
    ADD CONSTRAINT search_batch_info_pkey PRIMARY KEY (batch_id);


--
-- Name: search_links search_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_links
    ADD CONSTRAINT search_links_pkey PRIMARY KEY (link_id);


--
-- Name: search_queue search_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_queue
    ADD CONSTRAINT search_queue_pkey PRIMARY KEY (search_id);


--
-- Name: search_results search_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_results
    ADD CONSTRAINT search_results_pkey PRIMARY KEY (result_id);


--
-- Name: test_table test_table_pet_name_species_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_table
    ADD CONSTRAINT test_table_pet_name_species_key UNIQUE (pet_name, species);


--
-- Name: test_table test_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_table
    ADD CONSTRAINT test_table_pkey PRIMARY KEY (id);


--
-- Name: column_permission unique_column_permission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.column_permission
    ADD CONSTRAINT unique_column_permission UNIQUE (rc_id, relation_role);


--
-- Name: counties unique_fips; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.counties
    ADD CONSTRAINT unique_fips UNIQUE (fips);


--
-- Name: relation_column unique_relation_column; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.relation_column
    ADD CONSTRAINT unique_relation_column UNIQUE (relation, associated_column);


--
-- Name: link_data_sources_data_requests unique_source_request; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_data_sources_data_requests
    ADD CONSTRAINT unique_source_request UNIQUE (data_source_id, request_id);


--
-- Name: us_states unique_state_iso; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.us_states
    ADD CONSTRAINT unique_state_iso UNIQUE (state_iso);


--
-- Name: link_user_followed_location unique_user_location; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_user_followed_location
    ADD CONSTRAINT unique_user_location UNIQUE (user_id, location_id);


--
-- Name: us_states us_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.us_states
    ADD CONSTRAINT us_states_pkey PRIMARY KEY (id);


--
-- Name: user_notification_queue user_notification_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notification_queue
    ADD CONSTRAINT user_notification_queue_pkey PRIMARY KEY (id);


--
-- Name: user_permissions user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_pkey PRIMARY KEY (user_id, permission_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: recent_searches_expanded _RETURN; Type: RULE; Schema: public; Owner: -
--

CREATE OR REPLACE VIEW public.recent_searches_expanded AS
 SELECT rs.id,
    rs.user_id,
    rs.location_id,
    le.county_name,
    le.locality_name,
    le.type AS location_type,
    array_agg(rc.name) AS record_categories,
    le.state_name
   FROM (((public.recent_searches rs
     JOIN public.locations_expanded le ON ((rs.location_id = le.id)))
     JOIN public.link_recent_search_record_categories link ON ((link.recent_search_id = rs.id)))
     JOIN public.record_categories rc ON ((link.record_category_id = rc.id)))
  GROUP BY le.county_name, le.locality_name, le.type, le.state_name, rs.id;


--
-- Name: counties after_county_insert; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER after_county_insert AFTER INSERT ON public.counties FOR EACH ROW EXECUTE FUNCTION public.insert_county_location();


--
-- Name: TRIGGER after_county_insert ON counties; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER after_county_insert ON public.counties IS 'Inserts a new location of type "County" when a new county is added';


--
-- Name: localities after_locality_insert; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER after_locality_insert AFTER INSERT ON public.localities FOR EACH ROW EXECUTE FUNCTION public.insert_locality_location();


--
-- Name: TRIGGER after_locality_insert ON localities; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER after_locality_insert ON public.localities IS 'Inserts a new location of type "Locality" when a new locality is added';


--
-- Name: us_states after_state_insert; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER after_state_insert AFTER INSERT ON public.us_states FOR EACH ROW EXECUTE FUNCTION public.insert_state_location();


--
-- Name: TRIGGER after_state_insert ON us_states; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER after_state_insert ON public.us_states IS 'Inserts a new location of type "State" when a new state is added';


--
-- Name: recent_searches check_recent_searches_row_limit; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER check_recent_searches_row_limit BEFORE INSERT ON public.recent_searches FOR EACH ROW EXECUTE FUNCTION public.maintain_recent_searches_row_limit();


--
-- Name: TRIGGER check_recent_searches_row_limit ON recent_searches; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER check_recent_searches_row_limit ON public.recent_searches IS 'Executes `maintain_recent_searches_row_limit` prior to every insert';


--
-- Name: data_requests data_requests_status_change; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER data_requests_status_change BEFORE UPDATE ON public.data_requests FOR EACH ROW WHEN ((old.request_status IS DISTINCT FROM new.request_status)) EXECUTE FUNCTION public.update_status_change_date();


--
-- Name: TRIGGER data_requests_status_change ON data_requests; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER data_requests_status_change ON public.data_requests IS 'Updates date_status_last_changed whenever request_status changes.';


--
-- Name: data_sources insert_new_archive_info_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_new_archive_info_trigger AFTER INSERT ON public.data_sources FOR EACH ROW EXECUTE FUNCTION public.insert_new_archive_info();


--
-- Name: agencies set_agency_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER set_agency_updated_at BEFORE UPDATE ON public.agencies FOR EACH ROW EXECUTE FUNCTION public.update_airtable_agency_last_modified_column();


--
-- Name: data_sources set_data_source_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER set_data_source_updated_at BEFORE UPDATE ON public.data_sources FOR EACH ROW EXECUTE FUNCTION public.update_data_source_updated_at_column();


--
-- Name: data_sources set_source_name; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER set_source_name BEFORE INSERT ON public.data_sources FOR EACH ROW EXECUTE FUNCTION public.set_source_name();


--
-- Name: agencies trigger_set_agency_name; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_set_agency_name BEFORE INSERT OR UPDATE ON public.agencies FOR EACH ROW EXECUTE FUNCTION public.set_agency_name();


--
-- Name: TRIGGER trigger_set_agency_name ON agencies; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER trigger_set_agency_name ON public.agencies IS 'Calls `set_agency_name()` on inserts or updates to an Agency Row';


--
-- Name: search_results trigger_update_executed_datetime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_update_executed_datetime AFTER INSERT ON public.search_results FOR EACH ROW EXECUTE FUNCTION public.update_executed_datetime();


--
-- Name: search_results trigger_update_search_status; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_update_search_status AFTER INSERT ON public.search_results FOR EACH ROW EXECUTE FUNCTION public.update_search_status();


--
-- Name: data_sources update_approval_status_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_approval_status_updated_at BEFORE UPDATE ON public.data_sources FOR EACH ROW EXECUTE FUNCTION public.update_approval_status_updated_at();


--
-- Name: data_sources update_broken_source_url_as_of; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_broken_source_url_as_of BEFORE UPDATE ON public.data_sources FOR EACH ROW EXECUTE FUNCTION public.update_broken_source_url_as_of();


--
-- Name: agencies agencies_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agencies
    ADD CONSTRAINT agencies_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: link_agencies_data_sources agency_source_link_agency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_agencies_data_sources
    ADD CONSTRAINT agency_source_link_agency_id_fkey FOREIGN KEY (agency_id) REFERENCES public.agencies(id) ON DELETE CASCADE;


--
-- Name: link_agencies_data_sources agency_source_link_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_agencies_data_sources
    ADD CONSTRAINT agency_source_link_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id) ON DELETE CASCADE;


--
-- Name: agency_url_search_cache agency_url_search_cache_agency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agency_url_search_cache
    ADD CONSTRAINT agency_url_search_cache_agency_id_fkey FOREIGN KEY (agency_id) REFERENCES public.agencies(id);


--
-- Name: column_permission column_permission_rc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.column_permission
    ADD CONSTRAINT column_permission_rc_id_fkey FOREIGN KEY (rc_id) REFERENCES public.relation_column(id) ON DELETE CASCADE;


--
-- Name: counties counties_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.counties
    ADD CONSTRAINT counties_state_id_fkey FOREIGN KEY (state_id) REFERENCES public.us_states(id);


--
-- Name: data_requests data_requests_creator_user_id_fc; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests
    ADD CONSTRAINT data_requests_creator_user_id_fc FOREIGN KEY (creator_user_id) REFERENCES public.users(id);


--
-- Name: data_requests_github_issue_info data_requests_github_issue_info_data_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_requests_github_issue_info
    ADD CONSTRAINT data_requests_github_issue_info_data_request_id_fkey FOREIGN KEY (data_request_id) REFERENCES public.data_requests(id) ON DELETE CASCADE;


--
-- Name: data_sources_archive_info data_sources_archive_info_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources_archive_info
    ADD CONSTRAINT data_sources_archive_info_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id) ON DELETE CASCADE;


--
-- Name: data_sources data_sources_last_approval_editor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_last_approval_editor_fkey FOREIGN KEY (last_approval_editor) REFERENCES public.users(id);


--
-- Name: external_accounts external_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_accounts
    ADD CONSTRAINT external_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: data_sources fk_record_type; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT fk_record_type FOREIGN KEY (record_type_id) REFERENCES public.record_types(id);


--
-- Name: link_data_sources_data_requests link_data_sources_data_requests_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_data_sources_data_requests
    ADD CONSTRAINT link_data_sources_data_requests_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id) ON DELETE CASCADE;


--
-- Name: link_data_sources_data_requests link_data_sources_data_requests_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_data_sources_data_requests
    ADD CONSTRAINT link_data_sources_data_requests_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.data_requests(id) ON DELETE CASCADE;


--
-- Name: link_locations_data_requests link_locations_data_requests_data_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_locations_data_requests
    ADD CONSTRAINT link_locations_data_requests_data_request_id_fkey FOREIGN KEY (data_request_id) REFERENCES public.data_requests(id) ON DELETE CASCADE;


--
-- Name: link_locations_data_requests link_locations_data_requests_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_locations_data_requests
    ADD CONSTRAINT link_locations_data_requests_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: link_recent_search_record_categories link_recent_search_record_categories_recent_search_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_recent_search_record_categories
    ADD CONSTRAINT link_recent_search_record_categories_recent_search_id_fkey FOREIGN KEY (recent_search_id) REFERENCES public.recent_searches(id) ON DELETE CASCADE;


--
-- Name: link_recent_search_record_categories link_recent_search_record_categories_record_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_recent_search_record_categories
    ADD CONSTRAINT link_recent_search_record_categories_record_category_id_fkey FOREIGN KEY (record_category_id) REFERENCES public.record_categories(id) ON DELETE CASCADE;


--
-- Name: link_user_followed_location link_user_followed_location_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_user_followed_location
    ADD CONSTRAINT link_user_followed_location_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: link_user_followed_location link_user_followed_location_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_user_followed_location
    ADD CONSTRAINT link_user_followed_location_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: localities localities_county_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localities
    ADD CONSTRAINT localities_county_id_fkey FOREIGN KEY (county_id) REFERENCES public.counties(id);


--
-- Name: locations locations_county_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_county_id_fkey FOREIGN KEY (county_id) REFERENCES public.counties(id) ON DELETE CASCADE;


--
-- Name: locations locations_locality_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_locality_id_fkey FOREIGN KEY (locality_id) REFERENCES public.localities(id) ON DELETE CASCADE;


--
-- Name: locations locations_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_state_id_fkey FOREIGN KEY (state_id) REFERENCES public.us_states(id) ON DELETE CASCADE;


--
-- Name: recent_searches recent_searches_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recent_searches
    ADD CONSTRAINT recent_searches_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: recent_searches recent_searches_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recent_searches
    ADD CONSTRAINT recent_searches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: record_types record_types_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.record_types
    ADD CONSTRAINT record_types_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.record_categories(id);


--
-- Name: reset_tokens reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reset_tokens
    ADD CONSTRAINT reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: search_links search_links_search_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_links
    ADD CONSTRAINT search_links_search_id_fkey FOREIGN KEY (search_id) REFERENCES public.search_queue(search_id);


--
-- Name: search_queue search_queue_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_queue
    ADD CONSTRAINT search_queue_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.search_batch_info(batch_id);


--
-- Name: search_results search_results_search_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_results
    ADD CONSTRAINT search_results_search_id_fkey FOREIGN KEY (search_id) REFERENCES public.search_queue(search_id);


--
-- Name: user_notification_queue user_notification_queue_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notification_queue
    ADD CONSTRAINT user_notification_queue_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_permissions user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(permission_id);


--
-- Name: user_permissions user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

