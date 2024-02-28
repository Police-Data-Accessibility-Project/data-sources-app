import jwt
import os
import datetime


def login_results(cursor, email):
    cursor.execute(
        f"select id, password_digest, api_key from users where email = '{email}'"
    )
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "password_digest": results[0][1],
            "api_key": results[0][2],
        }
        return user_data
    else:
        return {"error": "no match"}


def is_admin(cursor, email):
    cursor.execute(f"select role from users where email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        role = results[0][0]
        if role == "admin":
            return True
        return False

    else:
        return {"error": "no match"}


def create_session_token(cursor, id, email):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=300)
    payload = {
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "sub": id,
    }
    session_token = jwt.encode(payload, os.getenv("secret_key"), algorithm="HS256")
    cursor.execute(
        f"insert into session_tokens (token, email, expiration_date) values ('{session_token}', '{email}', '{expiration}')"
    )

    return session_token


def token_results(cursor, token):
    cursor.execute(f"select id, email from session_tokens where token = '{token}'")
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "email": results[0][1],
        }
        return user_data
    else:
        return {"error": "no match"}
