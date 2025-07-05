import requests

from middleware.third_party_interaction_logic.mailgun_.constants import MAILGUN_URL, FROM_EMAIL
from middleware.util.env import get_env_variable


def send_via_mailgun(
    to_email: str,
    subject: str,
    text: str,
    html: str | None = None,
    bcc: str | None = None,
):
    """
    Sends an email via Mailgun
    :param to_email: The address to send the email to
    :param subject: The subject of the email
    :param text: The body of the email
    :param html: The HTML body of the email
    :param bcc: The address to BCC
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
        MAILGUN_URL,
        auth=(
            "api",
            get_env_variable("MAILGUN_KEY")
        ),
        data=data,
        timeout=5
    )

    r.raise_for_status()
