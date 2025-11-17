from db.helpers_.url_mappings.model import URLMapping


class URLMapper:

    def __init__(self, mappings: list[URLMapping]):
        self._url_to_id = {
            mapping.url: mapping.url_id
            for mapping in mappings
        }
        self._id_to_url = {
            mapping.url_id: mapping.url
            for mapping in mappings
        }

    def url_exists(self, url: str) -> bool:
        return url in self._url_to_id

    def id_exists(self, url_id: int) -> bool:
        return url_id in self._id_to_url

    def get_id(self, url: str) -> int:
        return self._url_to_id[url]

    def get_ids(self, urls: list[str]) -> list[int]:
        return [
            self._url_to_id[url]
            for url in urls
        ]

    def get_all_ids(self) -> list[int]:
        return list(self._url_to_id.values())

    def get_all_urls(self) -> list[str]:
        return list(self._url_to_id.keys())

    def get_url(self, url_id: int) -> str:
        return self._id_to_url[url_id]

    def get_mappings_by_url(self, urls: list[str]) -> list[URLMapping]:
        return [
            URLMapping(
                url_id=self._url_to_id[url],
                url=url
            ) for url in urls
        ]

    def add_mapping(self, mapping: URLMapping) -> None:
        self._url_to_id[mapping.url] = mapping.url_id
        self._id_to_url[mapping.url_id] = mapping.url

    def add_mappings(self, mappings: list[URLMapping]) -> None:
        for mapping in mappings:
            self.add_mapping(mapping)