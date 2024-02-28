import psycopg2
import os


def initialize_psycopg2_connection():
    try:
        DO_DATABASE_URL = os.getenv("DO_DATABASE_URL")

        return psycopg2.connect(
            DO_DATABASE_URL,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )

    except:
        print("Error while initializing the DigitalOcean client with psycopg2.")
        data_sources = {"count": 0, "data": []}

        return data_sources
