class LocationDoesNotExistError(Exception):
    pass


class DatabaseInitializationError(Exception):
    """
    Custom Exception to be raised when database connection initialization fails.
    """

    def __init__(self, message="Failed to initialize database connection."):
        self.message = message
        super().__init__(self.message)
