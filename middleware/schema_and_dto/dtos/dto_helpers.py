from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required
from middleware.schema_and_dto.dtos.common_dtos import GetManyResponseDTOBase


def create_get_many_dto(
    data_list_dto: type[BaseModel],
    description: str
) -> type[BaseModel]:

    class GetManyDTO(GetManyResponseDTOBase):
        data: list[data_list_dto] = default_field_required(description=description)

    GetManyDTO.__name__ = f"GetMany{data_list_dto.__name__}"

    return GetManyDTO