from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto_logic.dtos._helpers import default_field_not_required


class AgencyMatchRequestDTO(BaseModel):
    name: str = Field(
        description="The name of the agency to match.",
    )
    state: Optional[str] = default_field_not_required(
        "The state of the agency to match."
    )
    county: Optional[str] = default_field_not_required(
        description="The county of the agency to match.",
    )
    locality: Optional[str] = default_field_not_required(
        description="The locality of the agency to match.",
    )

    def has_location_data(self) -> bool:
        return (
            self.state is not None
            or self.county is not None
            or self.locality is not None
        )
