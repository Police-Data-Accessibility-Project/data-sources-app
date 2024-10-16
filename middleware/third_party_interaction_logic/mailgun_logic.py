import requests

from middleware.util import get_env_variable

MAILGUN_URL = "https://api.mailgun.net/v3/mail.pdap.io/messages"
FROM_EMAIL = "mail@pdap.io"

def send_via_mailgun(
    to_email: str,
    subject: str,
    body: str
):
    """
    Sends an email via Mailgun
    :param to_email: The address to send the email to
    :param subject: The subject of the email
    :param body: The body of the email
    :return:
    """
    r = requests.post(
        MAILGUN_URL,
        auth=("api", get_env_variable("MAILGUN_KEY")),
        data={
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": body
        },
        timeout=5
    )

    r.raise_for_status()