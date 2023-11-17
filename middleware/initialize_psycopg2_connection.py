import psycopg2
import os

QUICK_SEARCH_QUERY = """
    SELECT
        data_sources.airtable_uid,
        data_sources.name AS data_source_name,
        data_sources.description,
        data_sources.record_type,
        data_sources.source_url,
        data_sources.record_format,
        data_sources.coverage_start,
        data_sources.coverage_end,
        data_sources.agency_supplied,
        agencies.name AS agency_name,
        agencies.municipality,
        agencies.state_iso
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    INNER JOIN
        state_names ON agencies.state_iso = state_names.state_iso
    WHERE
        (data_sources.name ILIKE %s OR data_sources.description ILIKE %s OR data_sources.record_type ILIKE %s OR data_sources.tags ILIKE %s) 
        AND (agencies.county_name ILIKE %s OR concat(substr(agencies.county_name,3,length(agencies.county_name)-4), ' county') ILIKE %s 
            OR agencies.state_iso ILIKE %s OR agencies.municipality ILIKE %s OR agencies.agency_type ILIKE %s OR agencies.jurisdiction_type ILIKE %s 
            OR agencies.name ILIKE %s OR state_names.state_name ILIKE %s)
        AND data_sources.approval_status = 'approved'

"""

def initialize_psycopg2_connection():
    try:
        DO_DATABASE_URL = os.getenv('DO_DATABASE_URL')

        return psycopg2.connect(DO_DATABASE_URL)

    except:
        print('Error while initializing the DigitalOcean client with psycopg2.')
        data_sources = {'count': 0, 'data': []}

        return data_sources