from typing import Optional

from sqlalchemy import CheckConstraint, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class Locality(StandardBase):
    __tablename__ = Relations.LOCALITIES.value
    __table_args__ = (
        CheckConstraint("name NOT LIKE '%,%'", name="localities_name_check"),
    )

    name: Mapped[Optional[Text]] = mapped_column(Text)
    county_id: Mapped[int] = mapped_column(ForeignKey("counties.id"))

    # Relationships
    county = relationship("County", back_populates="localities", uselist=False)
    location = relationship("Location", back_populates="locality", uselist=False)
