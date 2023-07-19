from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from resources.User import User
from supabase_py import create_client
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)
CORS(app)

def read_env():
    try:
        with open('.env') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    except: 
        print('Cannot open file')
        file.close()

read_env()

def initialize_supabase_client():
    try:
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        print('Error while initializing the Supabase client.')
        raise

supabase = initialize_supabase_client()

api.add_resource(User, '/user', resource_class_kwargs={"bcrypt": bcrypt, "supabase": supabase})

@app.route('/sign-up/<email>/<password>')
def sign_up(email, password):
    res = supabase.auth.sign_up(email, password)
    return res

@app.route('/login/<email>/<password>')
def login(email, password):
    res = supabase.auth.sign_in(email, password)
    return res

@app.route('/sign-out')
def sign_out():
    res = supabase.auth.sign_out()
    return "Logged out"

@app.route('/quick-search/<search>/<county>')
def quick_search(search, county):
    try:
        data_sources = {'count': 0, 'data': []}

        # Query for all county_fips codes that match the county name searched
        counties = supabase.table('counties').select('fips').eq('name', county).execute()
        counties_fips = counties.get('data', []) 

        if len(counties_fips) > 0:
            # For each county_fip code, query for all agencies within that county and add to all agency list
            all_agencies = []
            for county_fips in counties_fips:
                fips = str(county_fips['fips'])
                agencies = supabase.table('agencies').select('name, municipality, state_iso, airtable_uid').eq('county_fips', fips).execute()
                agencies_data = agencies.get('data', [])
                for agency_data in agencies_data:
                    all_agencies.append(agency_data)
            
            # For each agency_uid, find all matches in the data_sources table that also have a partial match with the search term
            for agency in all_agencies:
                agency_data_sources = supabase.table('data_sources').select('name, description, record_type, source_url, record_format, coverage_start, coverage_end, agency_supplied').ilike('name', f"%{search}%").eq('agency_described', f"['{agency['airtable_uid']}']").execute()
                agency_data_sources_records = agency_data_sources.get('data')
                for record in agency_data_sources_records:
                    data_sources['count'] += 1
                    data_sources['data'].append({**record, **agency})
            return data_sources

        else:
            return data_sources
        
    except:
        print('Error during quick search operation')
        return data_sources

if __name__ == '__main__':
    app.run()