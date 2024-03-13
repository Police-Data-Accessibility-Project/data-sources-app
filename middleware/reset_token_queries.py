def check_reset_token(cursor, token):
    cursor.execute(
        f"select id, create_date, email from reset_tokens where token = '{token}'"
    )
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "create_date": results[0][1],
            "email": results[0][2],
        }
        return user_data
    else:
        return {"error": "no match"}


def add_reset_token(cursor, email, token):
    cursor.execute(
        f"insert into reset_tokens (email, token) values ('{email}', '{token}')"
    )

    return


def delete_reset_token(cursor, email, token):
    cursor.execute(
        f"delete from reset_tokens where email = '{email}' and token = '{token}'"
    )

    return
