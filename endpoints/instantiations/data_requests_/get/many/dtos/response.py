from endpoints.instantiations.data_requests_._shared.dtos.get import DataRequestsGetDTOBase
from middleware.schema_and_dto.dtos.dto_helpers import create_get_many_dto

GetManyDataRequestsResponseDTO = create_get_many_dto(
    data_list_dto=DataRequestsGetDTOBase,
    description="The list of data requests",
)