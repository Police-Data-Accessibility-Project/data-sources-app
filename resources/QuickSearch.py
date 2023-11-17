from flask_restful import Resource
from middleware.security import api_required
from utilities.common import convert_dates_to_strings, format_arrays
from middleware.initialize_psycopg2_connection import QUICK_SEARCH_QUERY
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
        
        search = "" if search == "all" else search
        location = "" if location == "all" else location

        # Depluralize search term to increase match potential
        nlp = spacy.load("en_core_web_sm")
        search = search.strip()
        doc = nlp(search)
        lemmatized_tokens = [token.lemma_ for token in doc]
        depluralized_search_term = " ".join(lemmatized_tokens)
        location = location.strip()

        cursor = self.psycopg2_connection.cursor()

        print(f"Query parameters: '%{depluralized_search_term}%', '%{location}%'")
     
        cursor.execute(QUICK_SEARCH_QUERY, (f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{depluralized_search_term}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%'))

        results = cursor.fetchall()
        # If altered search term returns no results, try with unaltered search term      
        if not results:
            print(f"Query parameters: '%{search}%', '%{location}%'")
            cursor.execute(QUICK_SEARCH_QUERY, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%'))
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
