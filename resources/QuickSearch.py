from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify, make_response
from middleware.security import api_required

class QuickSearch(Resource):
  def __init__(self, **kwargs):
    self.supabase = kwargs['supabase']
  
  # api_required decorator requires the request's header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
  # A user can get an API key by signing up and logging in (see User.py)
  @api_required
  def get(self, search, county):
    try:
        data_sources = {'count': 0, 'data': []}

        data_source_matches = self.supabase.table('agency_source_link').select('data_sources(data_source_name:name, description, record_type, source_url, record_format, coverage_start, coverage_end, agency_supplied), agencies(agency_name:name, municipality, state_iso)').ilike('data_sources.name', f"%{search}%").eq('agencies.county_name', f"[\"{county}\"]").execute()

        filtered_data_source_matches = [data_source_match for data_source_match in data_source_matches.data if data_source_match['agencies'] is not None and data_source_match['data_sources'] is not None]

        data_sources = {
            "count": len(filtered_data_source_matches),
            "data": [{**record["agencies"], **record['data_sources']} for record in filtered_data_source_matches]
        }

        return data_sources
        
    except:
        print('Error during quick search operation')
        return data_sources
