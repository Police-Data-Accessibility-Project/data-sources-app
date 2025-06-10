from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.implementations.core.record.category import RecordCategory
from db.models.templates.standard import StandardBase
from db.models.types import str_255, text
from middleware.enums import Relations


class RecordType(StandardBase):
    __tablename__ = Relations.RECORD_TYPES.value

    name: Mapped[str_255]
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[text]]

    # Relationships
    record_categories: Mapped[list[RecordCategory]] = relationship(
        argument="RecordCategory",
        back_populates="record_types",
    )
