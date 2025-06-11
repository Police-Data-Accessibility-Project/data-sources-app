from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from middleware.enums import Relations


class DependentLocation(Base):
    __tablename__ = Relations.DEPENDENT_LOCATIONS.value
    __mapper_args__ = {"primary_key": ["parent_location_id", "dependent_location_id"]}

    parent_location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    dependent_location_id: Mapped[int] = mapped_column(
        ForeignKey("public.locations.id")
    )
