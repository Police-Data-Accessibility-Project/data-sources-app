import datetime
import uuid


# DatabaseClient.insert_access_token()
def insert_access_token(cursor):
    token = uuid.uuid4().hex
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )
