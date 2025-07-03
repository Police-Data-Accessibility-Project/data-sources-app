class URLBuilder:
    """
    Builds URLs from a domain
    """

    def __init__(self, domain: str):
        self.domain = domain

    def build_url(self, subdirectory: str) -> str:
        return f"{self.domain}/{subdirectory}"
