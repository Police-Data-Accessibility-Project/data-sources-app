from middleware.enums import AccessTypeEnum


class ParserDeterminator:
    """
    Determines proper parser to use
    """

    def __init__(self, allowed_access_methods: list[AccessTypeEnum]):
        self.allowed_access_methods = allowed_access_methods

    def is_access_type_allowed(self, access_type: AccessTypeEnum) -> bool:
        return access_type in self.allowed_access_methods
