from middleware.initialize_supabase_client import initialize_supabase_client
from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
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
    "record_download_option_provided",
    "data_portal_type",
    "access_restrictions",
    "access_restrictions_notes",
    "record_format",
    "update_frequency",
    "update_method",
    "sort_method",
    "tags",
    "readme_url",
    "scraper_url",
    "state",
    "county",
    "municipality",
    "agency_type",
    "jurisdiction_type",
    "community_data_source",
    "data_source_created",
    "airtable_source_last_modified",
    "url_broken",
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
        self.supabase = kwargs['supabase']
    
    @api_required 
    def get(self):
        try:
            joined_column_names = ", ".join(approved_columns)
            response = self.supabase.table("data_sources").select(joined_column_names).eq("approved", "TRUE").execute()
            data = json.loads(response.json())
            data_sources = data['data']
            return data_sources
        
        except:
            return "There has been an error pulling data!"

