from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class StandardBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
