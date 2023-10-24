from flask_restful import Resource
from middleware.security import api_required
from utilities.common import convert_dates_to_strings, format_arrays
import spacy
import requests
import json
import os
import datetime

class QuickSearch(Resource):
  def __init__(self, **kwargs):
    self.psycopg2_connection = kwargs['psycopg2_connection']
  
  # api_required decorator requires the request's header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
  # A user can get an API key by signing up and logging in (see User.py)
  @api_required
  def get(self, search, location):
    try:
        data_sources = {'count': 0, 'data': []}
        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(search)
        lemmatized_tokens = [token.lemma_ for token in doc]
        depluralized_search_term = " ".join(lemmatized_tokens)

        cursor = self.psycopg2_connection.cursor()

        sql_query = """
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
            WHERE
                (data_sources.name ILIKE %s OR data_sources.description ILIKE %s OR data_sources.record_type ILIKE %s OR data_sources.tags ILIKE %s) AND (agencies.county_name ILIKE %s OR agencies.state_iso ILIKE %s OR agencies.municipality ILIKE %s OR agencies.agency_type ILIKE %s OR agencies.jurisdiction_type ILIKE %s OR agencies.name ILIKE %s)
        """

        cursor.execute(sql_query, (f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%'))

        results = cursor.fetchall()

        column_names = ['airtable_uid', 'data_source_name', 'description', 'record_type', 'source_url', 'record_format', 'coverage_start', 'coverage_end', 'agency_supplied', 'agency_name', 'municipality', 'state_iso']

        data_source_matches = [dict(zip(column_names, result)) for result in results]

        for item in data_source_matches:
           convert_dates_to_strings(item)
           format_arrays(item)

        data_sources = {
            "count": len(data_source_matches),
            "data": data_source_matches
        }

        current_datetime = datetime.datetime.now()
        datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        query_results = json.dumps(data_sources['data'])

        cursor_query_log = self.psycopg2_connection.cursor()
        sql_query_log = "INSERT INTO quick_search_query_logs (search, location, results, result_count, datetime_of_request) VALUES (%s, %s, %s, %s, %s)"
        cursor_query_log.execute(sql_query_log, (search, location, query_results, data_sources['count'], datetime_string))
        self.psycopg2_connection.commit()

        return data_sources
        
    except Exception as e:
        self.psycopg2_connection.rollback()
        print(str(e))
        webhook_url = os.getenv('WEBHOOK_URL')
        message = {'content': 'Error during quick search operation: ' + str(e) + "\n" + f"Search term: {search}\n" + f'Location: {location}'}
        requests.post(webhook_url, data=json.dumps(message), headers={"Content-Type": "application/json"})
        return data_sources
