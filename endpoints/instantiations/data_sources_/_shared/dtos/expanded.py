from typing import Optional

from endpoints.instantiations.data_sources_._shared.dtos.base import DataSourceBaseDTO
from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_not_required


class DataSourceExpandedDTO(DataSourceBaseDTO):
    record_type_name: Optional[RecordTypes] = default_field_not_required(
        description="The record type of the data source."
    )