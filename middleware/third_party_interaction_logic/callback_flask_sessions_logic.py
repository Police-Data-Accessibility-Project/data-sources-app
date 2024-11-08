"""
This file contains the logic for the Flask sessions in the callback logic.
Any logic which utilizes the `flask.session` import should be placed here.
`session` is a global variable within a given request context.
Consequently, care must be taken in both usage and testing of this logic.
"""
from typing import Optional

from flask import session

from middleware.enums import CallbackFunctionsEnum


# region Pre-Callback
def setup_callback_session(callback_functions_enum: CallbackFunctionsEnum, **kwargs):
    """
    Sets up the flask session that will be used for the callback function
    :param callback_functions_enum: the callback function to use
    :param kwargs: key-value parameters to pass to the callback function
    :return:
    """
    session["callback_function"] = callback_functions_enum.value
    session["callback_params"] = kwargs


# endregion Pre-Callback


# region Post-Callback
def get_callback_params() -> dict:
    """
    Returns the key-value parameters set prior to the callback function
    """
    callback_params = session.pop("callback_params", {})
    return callback_params


def get_callback_function() -> Optional[CallbackFunctionsEnum]:
    """
    Returns the callback function set prior to the callback function
    """
    callback_function_str = session.get("callback_function", None)
    return CallbackFunctionsEnum(callback_function_str)


# endregion Post-Callback
