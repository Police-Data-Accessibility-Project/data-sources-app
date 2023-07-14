from flask import Flask
from supabase_py import create_client
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/quick-search/<search>/<county>')
def quick_search(search, county):
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
        
        return all_agencies

    else:
        # Add error handling below
        return "No counties found"

if __name__ == '__main__':
    app.run()