from pydantic import BaseModel


class NestedDTOInfo(BaseModel):
    key: str
    class_: type
