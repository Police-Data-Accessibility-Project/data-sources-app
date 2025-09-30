from enum import Enum


class MetaURLCreationResponse(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ALREADY_EXISTS = "already_exists"
