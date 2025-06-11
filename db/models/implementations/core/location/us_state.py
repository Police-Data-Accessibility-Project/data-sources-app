from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class USState(StandardBase):
    __tablename__ = Relations.US_STATES.value

    state_iso: Mapped[str] = mapped_column(String(255), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255))

    # Relationships
    locations = relationship("Location", back_populates="state")
    counties = relationship("County", back_populates="state")
