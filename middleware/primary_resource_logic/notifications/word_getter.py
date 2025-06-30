class SingularPluralWordGetter:
    def __init__(self, items: list):
        self.is_plural = len(items) != 1

    def get_word(self, singular: str, plural: str) -> str:
        if self.is_plural:
            return plural
        return singular

    def get_past_tense_to_be(self):
        if self.is_plural:
            return "were"
        return "was"
