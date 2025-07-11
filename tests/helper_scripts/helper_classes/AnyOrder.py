class AnyOrder:
    """
    A helper object that compares equal to two arrays in any order
    """

    def __init__(self, list_: list):
        self.l = list_

    def __eq__(self, other: list) -> bool:
        return all(item in other for item in self.l)

    def __ne__(self, other):
        return not all(item in other for item in self.l)

    def __repr__(self):
        return "AnyOrder"
