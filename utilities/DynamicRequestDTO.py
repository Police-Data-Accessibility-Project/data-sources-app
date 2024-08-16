from flask import request


class DynamicRequestDTO:
    """
    Dynamic Request Data Transfer Object
    When instantiated, it will retrieve data from a flask request whose value matches the attributes provided to it.
    Additionally, transformation functions can be provided (with the nomenclature "_transform_<attribute_name>")
    which will transform the input data from its original format in the request to a format that the model expects.
    This object can then be used as a data transfer object for downstream functions.
    """

    def __init__(self):
        self._populate_attributes()

    def _populate_attributes(self):
        """
        Iterates through the attributes of the class and populates them with data from the request.
        """
        for attr_name in self.__annotations__:
            value = request.args.get(attr_name)
            transform = getattr(self, f"_transform_{attr_name}", None)
            if value is not None and callable(transform):
                value = transform(value)
            setattr(self, attr_name, value)
