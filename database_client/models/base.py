from datetime import date

from sqlalchemy import Text, DATE, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, DATERANGE
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import DeclarativeBase

from database_client.models.types import text, timestamp, daterange, str_255


class Base(DeclarativeBase):
    __table_args__ = {"schema": "public"}
    type_annotation_map = {
        text: Text,
        date: DATE,
        timestamp: TIMESTAMP,
        daterange: DATERANGE,
        str_255: String(255),
    }

    @hybrid_method
    def to_dict(cls, subquery_parameters=[]) -> dict:
        # Calls the class's __iter__ implementation
        dict_result = dict(cls)
        keyorder = cls.__mapper__.column_attrs.items()

        for param in subquery_parameters:
            if param.linking_column not in dict_result:
                dict_result[param.linking_column] = []

        sorted_dict = {
            col: dict_result[col] for col, descriptor in keyorder if col in dict_result
        }
        sorted_dict.update(dict_result)

        return sorted_dict
