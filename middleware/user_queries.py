from werkzeug.security import generate_password_hash


def user_get_results(cursor, email):
    cursor.execute(f"select id, password_digest from users where email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {"id": results[0][0], "password_digest": results[0][1]}
        return user_data
    else:
        return {"error": "no match"}


def user_post_results(cursor, email, password):
    password_digest = generate_password_hash(password)
    cursor.execute(
        f"insert into users (email, password_digest) values ('{email}', '{password_digest}')"
    )

    return
