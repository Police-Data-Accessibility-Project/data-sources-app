import psycopg2
import os

def initialize_psycopg2_connection():
    try:
        SUPABASE_DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
        if not SUPABASE_DATABASE_URL:
            SUPABASE_DATABASE_URL = config('SUPABASE_DATABASE_URL')

        return psycopg2.connect(SUPABASE_DATABASE_URL)
    except:
        print('Error while initializing the Supabase client with psycopg2.')
        data_sources = {'count': 0, 'data': []}

        return data_sources