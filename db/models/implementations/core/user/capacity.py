# pyright: reportUninitializedInstanceVariable=false
from sqlalchemy.orm import Mapped

from db.enums import UserCapacityEnum
from db.models.helpers import enum_column
from db.models.mixins import UserIDMixin
from db.models.templates.standard import StandardBase


class UserCapacity(StandardBase, UserIDMixin):
    __tablename__ = "user_capacities"

    capacity: Mapped[str] = enum_column(
        enum=UserCapacityEnum,
        name="user_capacities_enum",
    )