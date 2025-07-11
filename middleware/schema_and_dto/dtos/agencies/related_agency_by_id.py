from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO


class RelatedAgencyByIDDTO(GetByIDBaseDTO):
    agency_id: int

    def get_where_mapping(self):
        return {
            "data_source_id": int(self.resource_id),
            "agency_id": int(self.agency_id),
        }
