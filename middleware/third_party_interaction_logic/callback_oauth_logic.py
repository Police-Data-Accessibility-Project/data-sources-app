"""
This file contains the logic for the OAuth flow.
Any logic which utilizes the `oauth` import should be placed here.
Because it involves interactions with a third party app, the ability to test its logic is limited.
"""

from flask import url_for
from config import oauth


REDIRECT_ENDPOINT = "auth_callback"


def redirect_to_github_authorization():
    redirect_uri = url_for(
        endpoint=REDIRECT_ENDPOINT,
        _external=True,
    )
    return oauth.github.authorize_redirect(
        endpoint=redirect_uri,
    )


def get_github_user_email(token: str) -> str:
    """
    Gets the user email from the Github API via OAuth2
    :param token: The access token from the Github API
    :return: The user email
    """
    response = oauth.github.get("user/emails", token=token)
    response.raise_for_status()
    return response.json()[0]["email"]


def get_github_user_id(token: str) -> str:
    """
    Gets the user ID from the Github API via OAuth2
    :param token: The access token from the Github API
    :return: The user ID
    """
    response = oauth.github.get("user", token=token)
    response.raise_for_status()
    return response.json()["id"]


def get_github_oauth_access_token() -> str:
    """
    Gets the access token from the Github API via OAuth2
    :return: The access token
    """
    return oauth.github.authorize_access_token()
