# pyright: reportUninitializedInstanceVariable=false
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import OperationTypeLiteral
from middleware.enums import Relations


class ChangeLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.CHANGE_LOG.value

    operation_type: Mapped[OperationTypeLiteral]
    table_name: Mapped[str]
    affected_id: Mapped[int]
    old_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    new_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
