import datetime
import json
import re
from enum import Enum
from typing import Type, Union, Any

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from werkzeug.exceptions import BadRequest

from middleware.constants import DATETIME_FORMAT, DATE_FORMAT
from middleware.util.env import get_env_variable


def convert_dates_to_strings(data_dict: dict[str, Any]) -> dict:
    for key, value in data_dict.items():
        if isinstance(value, datetime.date):
            if key == "last_cached":
                data_dict[key] = value.strftime(DATETIME_FORMAT)
            else:
                data_dict[key] = value.strftime(DATE_FORMAT)
    return data_dict


def format_arrays(data_dict: dict[str, Any]):
    for key, value in data_dict.items():
        if value is not None and type(value) is str:
            if re.search(r"\"?\[ ?\".*\"\ ?]\"?", value, re.DOTALL):
                data_dict[key] = json.loads(value.strip('"'))
    return data_dict


def get_enums_from_string(
    enum_class: Type[Enum], comma_delimited_string: str, case_insensitive: bool = False
) -> Union[list[Enum], None]:
    # Split the input string into a list of names
    if len(comma_delimited_string) == 0:
        return None

    names = comma_delimited_string.split(",")

    # Strip any leading or trailing whitespace from the names
    names = [name.strip() for name in names]

    enum_values = [member.value for member in enum_class.__members__.values()]

    if case_insensitive:
        names = [name.lower() for name in names]
        enum_values = [name.lower() for name in enum_values]

    # Check for invalid names and raise an error if any are found
    invalid_names = [name for name in names if name not in enum_values]
    if invalid_names:
        raise ValueError(f"Invalid enum names: {', '.join(invalid_names)}")

    # Create a list of enums from the valid names
    result = [match_string_to_enum(name, enum_class) for name in names]

    return result


def match_string_to_enum(value: str, enum_class: Type[Enum]) -> Enum:
    # Convert input string to lowercase
    value_lower = value.lower()

    # Iterate through enum members and compare
    for member in enum_class:
        if member.value.lower() == value_lower:
            return member

    raise ValueError(
        f"'{value}' does not match any enum value in {enum_class.__name__}"
    )


def get_valid_enum_value(enum_type: Type[Enum], value: str) -> Enum:
    """
    Returns the appropriate enum value if it is valid, otherwise aborts the request.
    Must be within a Flask context
    :param enum_type:
    :param value:
    :return:
    """
    try:
        return match_string_to_enum(value, enum_type)
    except ValueError:
        raise BadRequest(
            f"Invalid {enum_type.__name__} '{value}'. Must be one of the following: {[item.value for item in enum_type]}"
        )


def get_alembic_conn_string() -> str:
    conn_string = get_env_variable("DO_DATABASE_URL")
    conn_string = conn_string.replace("postgresql", "postgresql+psycopg")
    return conn_string


def downgrade_to_base(alembic_cfg: Config, engine):
    try:
        command.downgrade(alembic_cfg, "base")
    except Exception as e:
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.commit()

        command.stamp(alembic_cfg, "base")
        raise e


def value_if_enum(entity: Any) -> Any:
    if isinstance(entity, Enum):
        return entity.value
    if isinstance(entity, list) and isinstance(entity[0], Enum):
        return [e.value for e in entity]
    return entity
