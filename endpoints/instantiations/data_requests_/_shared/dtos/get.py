from pydantic import BaseModel

from endpoints.instantiations.data_requests_._shared.dtos.base import DataRequestsBaseDTO
from endpoints.instantiations.data_sources_._shared.dtos.expanded import DataSourceExpandedDTO
from endpoints.instantiations.locations_._shared.dtos.response import LocationInfoResponseDTO
from middleware.schema_and_dto.dtos._helpers import default_field_required


class DataSourceLimitedDTO(BaseModel):
    id: str = default_field_required(description="The ID of the data source.")
    name: str = default_field_required(description="The name of the data source.")


class DataRequestsGetDTOBase(DataRequestsBaseDTO):
    data_sources: list[DataSourceLimitedDTO] = default_field_required(
        description="The data sources associated with the data request."
    )
    data_source_ids: list[int] = default_field_required(
        description="The data source ids associated with the data request."
    )
    locations: list[LocationInfoResponseDTO] = default_field_required(
        description="The locations associated with the data request"
    )
    location_ids: list[int] = default_field_required(
        description="The location ids associated with the data request"
    )