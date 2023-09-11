from flask_restful import Resource
from middleware.security import api_required
from utilities.convert_dates_to_strings import convert_dates_to_strings

class QuickSearch(Resource):
  def __init__(self, **kwargs):
    self.supabase = kwargs['supabase']
    self.psycopg2_connection = kwargs['psycopg2_connection']
  
  # api_required decorator requires the request's header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
  # A user can get an API key by signing up and logging in (see User.py)
  @api_required
  def get(self, search, county):
    try:
        data_sources = {'count': 0, 'data': []}

        cursor = self.psycopg2_connection.cursor()

        sql_query = """
            SELECT
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
            WHERE
                (data_sources.name ILIKE %s OR data_sources.description ILIKE %s OR data_sources.record_type ILIKE %s OR data_sources.tags ILIKE %s) AND (agencies.county_name ILIKE %s OR agencies.state_iso ILIKE %s OR agencies.municipality ILIKE %s OR agencies.agency_type ILIKE %s OR agencies.jurisdiction_type ILIKE %s OR agencies.name ILIKE %s)
        """

        cursor.execute(sql_query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{county}%', f'%{county}%', f'%{county}%', f'%{county}%', f'%{county}%', f'%{county}%'))

        results = cursor.fetchall()

        column_names = ['data_source_name', 'description', 'record_type', 'source_url', 'record_format', 'coverage_start', 'coverage_end', 'agency_supplied', 'agency_name', 'municipality', 'state_iso']

        data_source_matches = [dict(zip(column_names, result)) for result in results]

        for item in data_source_matches:
           convert_dates_to_strings(item)

        data_sources = {
            "count": len(data_source_matches),
            "data": data_source_matches
        }

        return data_sources
        
    except Exception as e:
        print('Error during quick search operation', str(e))
        return data_sources
