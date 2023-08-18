from supabase_py import create_client
import os

def initialize_supabase_client():
    try:
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        print('Error while initializing the Supabase client.')
        data_sources = {'count': 0, 'data': []}
        return data_sources