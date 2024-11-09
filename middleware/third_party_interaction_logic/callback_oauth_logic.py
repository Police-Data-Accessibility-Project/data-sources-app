"""
This file contains the logic for the OAuth flow.
Any logic which utilizes the `oauth` import should be placed here.
Because it involves interactions with a third party app, the ability to test its logic is limited.
"""
from typing import Optional
from github import Github, Auth

from config import oauth

REDIRECT_ENDPOINT = "auth_callback"


def redirect_to_github_authorization(
        redirect_url: Optional[str] = None
):
    return oauth.github.authorize_redirect(
        endpoint=redirect_url,
    )

def get_github_user_email(token: str) -> str:
    """
    Gets the user email from the Github API via OAuth2
    :param token: The access token from the Github API
    :return: The user email
    """
    auth = Auth.Token(token)
    g = Github(auth=auth)
    email_datas = g.get_user().get_emails()
    for email_data in email_datas:
        if email_data.primary is True:
            return email_data.email

    raise Exception("Primary email not found")


class BearerAuth:
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_github_user_id(token: str) -> int:
    """
    Gets the user ID from the Github API via OAuth2
    :param token: The access token from the Github API
    :return: The user ID
    """
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g.get_user().id



def get_github_oauth_access_token() -> dict:
    """
    Gets the access token from the Github API via OAuth2
    :return: The access token
    """
    return oauth.github.authorize_access_token()
