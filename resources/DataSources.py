from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from utilities.convert_dates_to_strings import convert_dates_to_strings
import json

approved_columns = [
    "name",
    "submitted_name",
    "description",
    "record_type",
    "source_url",
    "airtable_uid", 
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
    #"record_download_option_provided",
    "data_portal_type",
    #"access_restrictions",
    #"access_notes",
    "record_format",
    "update_frequency",
    "update_method",
    #"sort_method",
    "tags",
    "readme_url",
    "scraper_url",
    "state",
    "county",
    "municipality",
    "agency_type",
    "jurisdiction_type",
    #"community_data_source",
    "data_source_created",
    "airtable_source_last_modified",
    "url_status",
    "rejection_note",
    "last_approval_editor",
    "agency_described_submitted",
    "agency_described_not_in_database",
    "approved",
    "record_type_other",
    "data_portal_type_other",
    "records_not_online",
    "data_source_request",
    "url_button",
    "tags_other"
    ]

class DataSources(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']
    
    @api_required 
    def get(self):
        try:
            data_source_approved_columns = [f"data_sources.{approved_column}" for approved_column in approved_columns]
            data_source_approved_columns.append('agencies.name')

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
                    data_sources.approved = 'TRUE'
            """.format(joined_column_names)
            cursor.execute(sql_query)
            results = cursor.fetchall()

            approved_columns.append('agency_name')
            data_source_matches = [dict(zip(approved_columns, result)) for result in results]

            for item in data_source_matches:
                convert_dates_to_strings(item)

            data_sources = {
                "count": len(data_source_matches),
                "data": data_source_matches
            }
        
            return data_sources
        
        except Exception as e:
            print(str(e))
            return "There has been an error pulling data!"

