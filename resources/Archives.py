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
            sql_query = 'SELECT id, source_url, update_frequency, agency_name, last_cached FROM test_data_sources WHERE (last_cached IS NULL OR update_frequency IS NOT NULL) AND broken_source_url_as_of IS NULL'
            cursor.execute(sql_query)
            results = cursor.fetchall()

            column_names = ['id', 'source_url', 'update_frequency', 'agency_name', 'last_cached']

            archive_results = [dict(zip(column_names, result)) for result in results]

            for item in archive_results:
              convert_dates_to_strings(item)

            return archive_results
        
        except:
            return "There has been an error pulling data!"
        
    @api_required 
    def put(self):
        try:
            json_data = request.get_json()
            data = json.loads(json_data)

            cursor = self.psycopg2_connection.cursor()

            if data['broken_source_url_as_of']:
                sql_query = 'UPDATE test_data_sources SET broken_source_url_as_of = %s AND last_cached = %s WHERE id = %s'
                cursor.execute(sql_query, (data['broken_source_url_as_of'], data['last_cached'], data['id']))
            else:
                sql_query = 'UPDATE test_data_sources SET last_cached = %s WHERE id = %s'
                cursor.execute(sql_query, (data['last_cached'], data['id']))

            self.psycopg2_connection.commit()
            cursor.close()

            return {'status': 'success'}
        
        except Exception as e:
            return {'error': str(e)}