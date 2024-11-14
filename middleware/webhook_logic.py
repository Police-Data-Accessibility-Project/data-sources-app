import json
import os

import requests

from middleware.third_party_interaction_logic.mailgun_logic import send_via_mailgun
from middleware.util import get_env_variable


def post_to_webhook(msg: str):
    vite_vue_app_base_url = get_env_variable("VITE_VUE_APP_BASE_URL")
    webhook_url = get_env_variable("WEBHOOK_URL")

    requests.post(
        url=webhook_url,
        data=f"({vite_vue_app_base_url}) {msg}",
        headers={"Content-Type": "application/json"},
        timeout=5,
    )


def send_password_reset_link(email, token):
    body = (
        f"To reset your password, click the following link: "
        f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/reset-password?token={token}"
    )
    send_via_mailgun(
        to_email=email,
        subject="PDAP Data Sources Reset Password",
        text=body,
    )
