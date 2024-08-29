from dataclasses import dataclass

from middleware.enums import CallbackFunctionsEnum


@dataclass
class GithubUserInfo:
    """
    Information about a Github user
    """

    user_id: str
    user_email: str


@dataclass
class FlaskSessionCallbackInfo:
    """
    Contains information contained in the Flask session in the callback logic
    """

    callback_functions_enum: CallbackFunctionsEnum
    callback_params: dict


@dataclass
class OAuthCallbackInfo:
    """
    Contains information returned by OAuth in the callback logic
    """

    github_user_info: GithubUserInfo


@dataclass
class EntryDataRequest:
    """
    Contains data for creating or updating an entry
    """
    entry_data: dict


class DeferredFunction:
    """
    Encapsulates a function and its parameters for deferred execution.
    """

    def __init__(self, function: callable, **base_parameters):
        self.function = function
        self.base_parameters = base_parameters

    def execute(self, **additional_parameters):
        return self.function(**self.base_parameters, **additional_parameters)