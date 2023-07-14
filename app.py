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

    return counties_fips

if __name__ == '__main__':
    app.run()