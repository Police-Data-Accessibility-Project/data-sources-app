import requests

from middleware.util import get_env_variable


class DiscordPoster:

    def __init__(self):
        self.webhook_url = get_env_variable("WEBHOOK_URL")

    def post_to_discord(self, message):
        requests.post(self.webhook_url, json={"content": message}, timeout=5)
