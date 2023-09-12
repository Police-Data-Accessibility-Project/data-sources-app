from middleware.initialize_supabase_client import initialize_supabase_client
from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
import json

approved_columns = [
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
        "defunct_year",
        "airtable_uid",
    ]

class Agencies(Resource):
    def __init__(self, **kwargs):
        self.supabase = kwargs['supabase']
    
    @api_required 
    def get(self):
        try:
            joined_column_names = ", ".join(approved_columns)
            response = self.supabase.table("agencies").select(joined_column_names).eq("approved", "TRUE").execute()
            data = json.loads(response.json())
            agencies = data['data']
            return agencies
        
        except:
            return "There has been an error pulling data!"

