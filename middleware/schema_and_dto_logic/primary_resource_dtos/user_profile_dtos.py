from dataclasses import dataclass


@dataclass
class UserPutDTO:
    old_password: str
    new_password: str
