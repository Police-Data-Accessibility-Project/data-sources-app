from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from resources.User import User
from resources.QuickSearch import QuickSearch
from resources.DataSources import DataSources
from middleware.initialize_supabase_client import initialize_supabase_client
import os

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

read_env()
supabase = initialize_supabase_client()

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(User, '/user', resource_class_kwargs={"supabase": supabase})
api.add_resource(QuickSearch, '/quick-search/<search>/<county>', resource_class_kwargs={"supabase": supabase})
api.add_resource(DataSources, '/data-sources', resource_class_kwargs={"supabase": supabase})

if __name__ == '__main__':
    app.run(debug=True)
