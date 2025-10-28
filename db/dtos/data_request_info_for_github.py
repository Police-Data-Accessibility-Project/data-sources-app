from pydantic import BaseModel

from middleware.enums import RecordTypesEnum


class DataRequestInfoForGithub(BaseModel):
    """
    Data Request Info to be used in the creation of GitHub Issues
    """

    id: int
    title: str
    submission_notes: str
    data_requirements: str
    locations: list[str] | None
    record_types: list[RecordTypesEnum] | None
