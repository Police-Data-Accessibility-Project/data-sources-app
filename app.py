from flask import Flask
from supabase_py import create_client
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def test():
    result = supabase.table('data_sources').select("*").execute()
    data = result.get('data', [])
    return data

if __name__ == '__main__':
    app.run()