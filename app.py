from collections.abc import Mapping
from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from resources.User import User
from resources.QuickSearch import QuickSearch
from supabase_py import create_client
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)
CORS(app)

def read_env():
    app_env = os.environ.get('APP_ENV', 'local')
    
    if app_env == 'local':
        try:
            with open('.env') as file:
                for line in file:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        except FileNotFoundError:
            print("The '.env' file was not found. Please create the file and set the necessary environment variables.")
            data_sources = {'count': 0, 'data': []}
            return data_sources
        except: 
            print('Cannot open file')
            file.close()
            data_sources = {'count': 0, 'data': []}
            return data_sources

def initialize_supabase_client():
    try:
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        print('Error while initializing the Supabase client.')
        data_sources = {'count': 0, 'data': []}
        return data_sources

read_env()
supabase = initialize_supabase_client()

api.add_resource(User, '/user', resource_class_kwargs={"bcrypt": bcrypt, "supabase": supabase})
api.add_resource(QuickSearch, '/quick-search/<search>/<county>', resource_class_kwargs={"bcrypt": bcrypt, "supabase": supabase})

if __name__ == '__main__':
    app.run()
