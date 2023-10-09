from middleware.security import api_required
from flask_restful import Resource, request
from utilities.convert_dates_to_strings import convert_dates_to_strings
import json

class Archives(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']
    
    @api_required 
    def get(self):
        try:
            cursor = self.psycopg2_connection.cursor()
            sql_query = '''
            SELECT
                data_sources.airtable_uid,
                data_sources.source_url,
                data_sources.update_frequency,
                data_sources.last_cached,
                agencies.name
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE 
                (data_sources.last_cached IS NULL OR data_sources.update_frequency IS NOT NULL) AND data_sources.broken_source_url_as_of IS NULL AND data_sources.source_url IS NOT NULL
            '''
            cursor.execute(sql_query)
            results = cursor.fetchall()

            column_names = ['id', 'source_url', 'update_frequency', 'last_cached', 'agency_name']

            archive_results = [dict(zip(column_names, result)) for result in results]

            for item in archive_results:
                convert_dates_to_strings(item)

            return archive_results
        
        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return "There has been an error pulling data!"
        
    @api_required 
    def put(self):
        try:
            json_data = request.get_json()
            data = json.loads(json_data)

            cursor = self.psycopg2_connection.cursor()

            if data['broken_source_url_as_of']:
                sql_query = 'UPDATE data_sources SET broken_source_url_as_of = %s AND last_cached = %s WHERE airtable_uid = %s'
                cursor.execute(sql_query, (data['broken_source_url_as_of'], data['last_cached'], data['id']))
            else:
                sql_query = 'UPDATE data_sources SET last_cached = %s WHERE airtable_uid = %s'
                cursor.execute(sql_query, (data['last_cached'], data['id']))

            self.psycopg2_connection.commit()
            cursor.close()

            return {'status': 'success'}
        
        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {'error': str(e)}