from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from utilities.common import convert_dates_to_strings, format_arrays
import json

approved_columns = [
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
    "update_frequency",
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
    "tags_other"
    ]

agency_approved_columns = [
    "name",
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
    "defunct_year"
]

class DataSourceById(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']
    
    @api_required
    def get(self, data_source_id):
        try:
            data_source_approved_columns = [f"data_sources.{approved_column}" for approved_column in approved_columns]
            agencies_approved_columns = [f"agencies.{field}" for field in agency_approved_columns]
            all_approved_columns = data_source_approved_columns + agencies_approved_columns
            all_approved_columns.append("data_sources.airtable_uid as data_source_id")
            all_approved_columns.append("agencies.airtable_uid as agency_id")

            joined_column_names = ", ".join(all_approved_columns)

            cursor = self.psycopg2_connection.cursor()
            sql_query = """
                SELECT
                    {}
                FROM
                    agency_source_link
                INNER JOIN
                    data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
                INNER JOIN
                    agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
                WHERE
                    data_sources.approved = 'TRUE' AND data_sources.airtable_uid = %s
            """.format(joined_column_names)
            cursor.execute(sql_query, (data_source_id,))
            result = cursor.fetchone()

            if result:
                data_source_and_agency_columns = approved_columns + agency_approved_columns
                data_source_and_agency_columns.append("data_source_id")
                data_source_and_agency_columns.append("agency_id")
                data_source_details = dict(zip(data_source_and_agency_columns, result))
                convert_dates_to_strings(data_source_details)
                format_arrays(data_source_details)
                return data_source_details
            else:
                return "Data source not found.", 404
        
        except Exception as e:
            print(str(e))
            return "There has been an error pulling data!"
    
class DataSources(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']

    @api_required 
    def get(self):
        try:
            data_source_approved_columns = [f"data_sources.{approved_column}" for approved_column in approved_columns]
            data_source_approved_columns.append('agencies.name as agency_name')

            joined_column_names = ", ".join(data_source_approved_columns)

            cursor = self.psycopg2_connection.cursor()
            sql_query = """
                SELECT
                    {}
                FROM
                    agency_source_link
                INNER JOIN
                    data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
                INNER JOIN
                    agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
                WHERE
                    data_sources.approval_status = 'approved'
            """.format(joined_column_names)
            cursor.execute(sql_query)
            results = cursor.fetchall()

            data_source_output_columns = approved_columns + ['agency_name']
            data_source_matches = [dict(zip(data_source_output_columns, result)) for result in results]

            for item in data_source_matches:
                convert_dates_to_strings(item)

            data_sources = {
                "count": len(data_source_matches),
                "data": data_source_matches
            }
        
            return data_sources
        
        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return "There has been an error pulling data!"

