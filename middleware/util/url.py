import re

from middleware.util.env import get_env_variable


def normalize_url(source_url: str) -> str:
    # Remove 'https://', 'http://' from the beginning
    url = re.sub(r"^(https://|http://)", "", source_url)
    # Remove "www." from the beginning
    url = re.sub(r"^www\.", "", url)
    # Remove trailing '/'
    url = url.rstrip("/")

    return url


def create_web_app_url(endpoint: str) -> str:
    return f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/{endpoint}"
