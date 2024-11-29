from dataclasses import dataclass


@dataclass
class RequestResetPasswordRequestDTO:
    email: str
    token: str


@dataclass
class ResetPasswordDTO:
    password: str
