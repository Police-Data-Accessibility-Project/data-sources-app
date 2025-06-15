from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from middleware.util.type_conversion import stringify_lists

"""
`Simple` in this case refers to helper functions 
which rely on no external dependencies
"""


def get_authorization_header(
    scheme: str,
    token: str,
) -> dict:
    return {"Authorization": f"{scheme} {token}"}


def add_query_params(url, params: dict):
    """
    Add query parameters to a URL.
    :param url:
    :param params:
    :return:
    """

    # Remove all parameters that are none
    params = {k: v for k, v in params.items() if v is not None}

    stringify_lists(d=params)

    # Parse the original URL into components
    url_parts = list(urlparse(url))

    # Extract existing query parameters (if any) and update with the new ones
    query = dict(parse_qs(url_parts[4]))
    query.update(params)

    # Encode the updated query parameters
    url_parts[4] = urlencode(query, doseq=True)

    # Rebuild the URL with the updated query parameters
    return urlunparse(url_parts)


def get_notification_valid_date():
    return datetime.now(timezone.utc) - timedelta(days=25)
