class UserNotFoundError(Exception):
    """Exception raised for errors in the input."""

    def __init__(
        self, identifier: str, message: str = "", identifier_name: str = "email"
    ):
        if message == "":
            message = f"User with {identifier_name} {identifier} not found"
        self.identifier = identifier
        self.message = message.format(email=self.identifier)
        super().__init__(self.message)


class DuplicateUserError(Exception):
    pass


class InvalidAPIKeyException(Exception):
    pass


class InvalidAuthorizationHeaderException(Exception):
    pass
