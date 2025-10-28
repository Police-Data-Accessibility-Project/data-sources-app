# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.helpers import enum_column
from db.models.implementations.core.record.category import RecordCategory
from db.models.templates.standard import StandardBase
from db.models.types import text
from middleware.enums import Relations, RecordTypesEnum


class RecordType(StandardBase):
    __tablename__ = Relations.RECORD_TYPES.value

    name: Mapped[RecordTypesEnum] = enum_column(RecordTypesEnum, name="record_type")
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[text | None]

    # Relationships
    record_category: Mapped[RecordCategory] = relationship(
        argument="RecordCategory",
        back_populates="record_types",
        uselist=False,
    )
