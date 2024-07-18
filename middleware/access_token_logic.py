import datetime
import uuid

from database_client.database_client import DatabaseClient


def insert_access_token(db_client: DatabaseClient):
    token = uuid.uuid4().hex
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    db_client.add_new_access_token(token, expiration)
