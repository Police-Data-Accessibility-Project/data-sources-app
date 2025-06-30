class AttributeNotInClassError(Exception):
    def __init__(self, attribute: str, class_name: str):
        super().__init__(
            f"The attribute '{attribute}' is not part of the class '{class_name}'"
        )


class MissingArgumentError(Exception):
    pass
