from typing import Optional

from middleware.util.argument_checking import check_for_mutually_exclusive_arguments


class ResponseInfo:
    """
    A configuration dataclasses for defining common information in a response
    """

    def __init__(
        self,
        success_message: Optional[str] = None,
        response_dictionary: Optional[dict] = None,
    ):
        check_for_mutually_exclusive_arguments(
            arg1=success_message, arg2=response_dictionary
        )

        self.success_message = success_message
        self.response_dictionary = response_dictionary
