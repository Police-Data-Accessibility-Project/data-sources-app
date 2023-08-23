from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify, make_response
from middleware.security import api_required

class QuickSearch(Resource):
  def __init__(self, **kwargs):
    self.supabase = kwargs['supabase']
  
  @api_required
  def get(self, search, county):
    try:
        data_sources = {'count': 0, 'data': []}

        # Query for all county_fips codes that match the county name searched
        counties = self.supabase.table('counties').select('fips').eq('name', county).execute()
        counties_fips = counties.data

        if len(counties_fips) > 0:
            # For each county_fip code, query for all agencies within that county and add to all agency list
            all_agencies = []
            for county_fips in counties_fips:
                fips = str(county_fips['fips'])
                agencies = self.supabase.table('agencies').select('name, municipality, state_iso, airtable_uid').eq('county_fips', fips).execute()                
                agencies_data = agencies.data
                
                for agency_data in agencies_data:
                    all_agencies.append({**agency_data, "agency_name": agency_data.pop('name')})

            # For each agency_uid, find all agency and data source pairs that match the agency airtable_uid
            for agency in all_agencies:
                agency_airtable_uid = agency['airtable_uid']
                agency_data_sources = self.supabase.table('agency_source_link').select('*').eq('agency_described_linked_uid', agency_airtable_uid).execute()
                agency_data_sources_records = agency_data_sources.data

                for agency_data_sources_record in agency_data_sources_records:
                    data_source_matches = self.supabase.table('data_sources').select('name, description, record_type, source_url, record_format, coverage_start, coverage_end, agency_supplied').ilike('name', f"%{search}%").eq('airtable_uid', agency_data_sources_record['airtable_uid']).execute()
                    data_source_matches_data = data_source_matches.data

                    for record in data_source_matches_data:
                        data_sources['count'] += 1
                        data_sources['data'].append({**record, **agency, "data_source_name": record.pop('name')})
            return data_sources

        else:
            return data_sources
        
    except:
        print('Error during quick search operation')
        return data_sources
