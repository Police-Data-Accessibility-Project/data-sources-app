from typing import Optional

from sqlalchemy.orm import Mapped, relationship

from db.models.templates.standard import StandardBase
from db.models.types import str_255, text
from middleware.enums import Relations


class RecordCategory(StandardBase):
    __tablename__ = Relations.RECORD_CATEGORIES.value

    # TODO: Update so that names reference literals
    name: Mapped[str_255]
    description: Mapped[Optional[text]]

    # Relationships
    record_types: Mapped[list["RecordType"]] = relationship(
        argument="RecordType",
        back_populates="record_categories",
    )
