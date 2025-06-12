class LocationDoesNotExistError(Exception):
    pass


class DatabaseInitializationError(Exception):
    """
    Custom Exception to be raised when psycopg connection initialization fails.
    """

    def __init__(self, message="Failed to initialize psycopg connection."):
        self.message = message
        super().__init__(self.message)
