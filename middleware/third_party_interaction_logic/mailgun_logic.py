from typing import Optional

import requests

from middleware.util import get_env_variable

MAILGUN_URL = "https://api.mailgun.net/v3/mail.pdap.io/messages"
FROM_EMAIL = "mail@pdap.io"


def send_via_mailgun(
    to_email: str,
    subject: str,
    text: str,
    html: Optional[str] = None,
    bcc: Optional[str] = None,
):
    """
    Sends an email via Mailgun
    :param to_email: The address to send the email to
    :param subject: The subject of the email
    :param text: The body of the email
    :return:
    """
    data = {
        "from": f"PDAP Notifications <{FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "text": text,
    }

    if html is not None:
        data["html"] = html
    if bcc is not None:
        data["bcc"] = bcc

    r = requests.post(
        MAILGUN_URL, auth=("api", get_env_variable("MAILGUN_KEY")), data=data, timeout=5
    )

    r.raise_for_status()
