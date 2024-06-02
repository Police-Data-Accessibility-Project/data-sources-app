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
