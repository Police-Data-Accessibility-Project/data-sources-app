from enum import Enum


class CallbackFunctionsEnum(Enum):
    """
    Enums for the callback_wrapper function, to determine
    which callback function to use.
    """
    LOGIN_WITH_GITHUB = "login_user_with_github"
    CREATE_USER_WITH_GITHUB = "register_user"
    LINK_TO_GITHUB = "link_to_github"
