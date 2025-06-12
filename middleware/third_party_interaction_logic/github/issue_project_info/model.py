from pydantic import BaseModel

from middleware.enums import RecordTypes


class GIPIInfo(BaseModel):
    project_status: str
    record_types: list[RecordTypes]

    def record_types_as_list_of_strings(self) -> list[str]:
        return [record_type.value for record_type in self.record_types]
