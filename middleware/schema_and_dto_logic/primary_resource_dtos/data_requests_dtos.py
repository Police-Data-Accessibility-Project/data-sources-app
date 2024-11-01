from dataclasses import dataclass
from typing import Optional

from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType, RequestStatus
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


@dataclass
class DataRequestLocationInfoPostDTO:
    type: LocationType
    state: str
    county: Optional[str] = None
    locality: Optional[str] = None

    def get_where_mappings(self) -> list[WhereMapping]:
        d =  {
            "type": self.type,
            "state": self.state,
        }
        if self.county is not None:
            d["county"] = self.county
        if self.locality is not None:
            d["locality"] = self.locality
        return WhereMapping.from_dict(d)

@dataclass
class GetManyDataRequestsRequestsDTO(GetManyBaseDTO):
    request_status: Optional[RequestStatus] = None