from pydantic import BaseModel

from db.enums import URLStatus


class MetaURLSyncContentModel(BaseModel):
    url: str
    url_status: URLStatus = URLStatus.OK
    internet_archive_url: str | None = None
    agency_ids: list[int]
