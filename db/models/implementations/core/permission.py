# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy.orm import Mapped

from db.models.templates.standard import StandardBase
from db.models.types import str_255, text
from middleware.enums import Relations


class Permission(StandardBase):
    __tablename__ = Relations.PERMISSIONS.value

    permission_name: Mapped[str_255]
    description: Mapped[text | None]
