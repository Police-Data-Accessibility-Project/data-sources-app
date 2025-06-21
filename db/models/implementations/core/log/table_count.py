# pyright: reportUninitializedInstanceVariable=false
from sqlalchemy.orm import Mapped

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class TableCountLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.TABLE_COUNT_LOG.value

    table_name: Mapped[str]
    count: Mapped[int]
