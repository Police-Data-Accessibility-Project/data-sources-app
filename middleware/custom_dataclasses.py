from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from db.enums import EntityType, EventType
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

    callback_functions_enum: Optional[CallbackFunctionsEnum]
    callback_params: dict


class OAuthCallbackInfo(BaseModel):
    """
    Contains information returned by OAuth in the callback logic
    """

    github_user_info: GithubUserInfo


class DeferredFunction:
    """
    Encapsulates a function and its parameters for deferred execution.
    """

    def __init__(self, function: callable, **base_parameters):
        self.function = function
        self.base_parameters = base_parameters

    def execute(self, **additional_parameters):
        return self.function(**self.base_parameters, **additional_parameters)


@dataclass
class EventInfo:
    """
    Information about an event
    """

    event_id: int
    event_type: EventType
    entity_id: int
    entity_type: EntityType
    entity_name: str


@dataclass
class EventBatch:
    """
    A batch of events
    """

    user_id: int
    user_email: str
    events: list[EventInfo]

    def get_events_of_type(self, event_type: EventType):
        return [event for event in self.events if event.event_type == event_type]
