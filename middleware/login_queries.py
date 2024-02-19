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
