from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from resources.User import User
from resources.QuickSearch import QuickSearch
from resources.DataSources import DataSources
from middleware.initialize_supabase_client import initialize_supabase_client
import os


supabase = initialize_supabase_client()

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(User, '/user', resource_class_kwargs={"supabase": supabase})
api.add_resource(QuickSearch, '/quick-search/<search>/<county>', resource_class_kwargs={"supabase": supabase})
api.add_resource(DataSources, '/data-sources', resource_class_kwargs={"supabase": supabase})

if __name__ == '__main__':
    app.run(debug=True)
