import psycopg2
import os

def initialize_psycopg2_connection():
    try:
        DO_DATABASE_URL = os.getenv('DO_DATABASE_URL')

        return psycopg2.connect(DO_DATABASE_URL)

    except:
        print('Error while initializing the DigitalOcean client with psycopg2.')
        data_sources = {'count': 0, 'data': []}

        return data_sources