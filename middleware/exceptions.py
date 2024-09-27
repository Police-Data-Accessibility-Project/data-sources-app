class UserNotFoundError(Exception):
    """Exception raised for errors in the input."""

    def __init__(self, email, message=""):
        if message == "":
            message = f"User with email {email} not found"
        self.email = email
        self.message = message.format(email=self.email)
        super().__init__(self.message)

class DuplicateUserError(Exception):
    pass

class TokenNotFoundError(Exception):
    """Raised when the token is not found in the database."""

    pass


class AccessTokenNotFoundError(Exception):
    pass


class InvalidAPIKeyException(Exception):
    pass


class InvalidAuthorizationHeaderException(Exception):
    pass
