import json
import os

import requests


def post_to_webhook(data: str):
    webhook_url = os.getenv("WEBHOOK_URL")

    requests.post(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
    )


def send_password_reset_link(email, token):
    body = f"To reset your password, click the following link: {os.getenv('VITE_VUE_APP_BASE_URL')}/reset-password/{token}"
    r = requests.post(
        "https://api.mailgun.net/v3/mail.pdap.io/messages",
        auth=("api", os.getenv("MAILGUN_KEY")),
        data={
            "from": "mail@pdap.io",
            "to": [email],
            "subject": "PDAP Data Sources Reset Password",
            "text": body,
        },
    )
