from dataclasses import dataclass

from pydantic import BaseModel

from middleware.enums import CallbackFunctionsEnum


class GithubUserInfo(BaseModel):
    """
    Information about a Github user
    """

    user_id: int
    user_email: str


@dataclass
class FlaskSessionCallbackInfo:
    """
    Contains information contained in the Flask session in the callback logic
    """

    callback_functions_enum: CallbackFunctionsEnum | None
    callback_params: dict


class DeferredFunction:
    """
    Encapsulates a function and its parameters for deferred execution.
    """

    def __init__(self, function: callable, **base_parameters):
        self.function = function
        self.base_parameters = base_parameters

    def execute(self, **additional_parameters):
        return self.function(**self.base_parameters, **additional_parameters)
