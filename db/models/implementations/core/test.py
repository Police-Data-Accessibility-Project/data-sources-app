# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy.orm import Mapped

from db.models.templates.standard import StandardBase
from db.models.types import str_255
from middleware.enums import Relations


class TestTable(StandardBase):
    __tablename__ = Relations.TEST_TABLE.value

    pet_name: Mapped[str_255 | None]
    species: Mapped[str_255 | None]
