import psycopg2

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api


def test_request_reset_password_post(
    client_with_db, dev_db_connection: psycopg2.extensions.connection, mocker
):

    user_info = create_test_user_api(client_with_db)

    mock_post = mocker.patch("resources.RequestResetPassword.requests.post")
    response = client_with_db.post(
        "/request-reset-password", json={"email": user_info.email}
    )
    reset_token = response.json.get("token")
    assert (
        response.status_code == 200
    ), "Request to Reset Password request was not returned successfully"
    assert mock_post.call_count == 1, "request.post should be called only once"
    assert (
        mock_post.call_args[0][0] == "https://api.mailgun.net/v3/mail.pdap.io/messages"
    )


    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
    SELECT email FROM reset_tokens where token = %s
    """,
        (reset_token,),
    )
    rows = cursor.fetchall()
    assert (
        len(rows) == 1
    ), "Only one row should have a reset token associated with this email"
    email = rows[0][0]
    assert (
        email == user_info.email
    ), "Email associated with reset token should match the user's email"
