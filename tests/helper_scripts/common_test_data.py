import random
import uuid
from enum import Enum


def get_random_boolean() -> bool:
    return random.choice([True, False])


def get_random_possible_enum_value(enum: Enum) -> str:
    return random.choice(list(enum)).value


def get_random_number_for_testing():
    number = random.randint(1, 999999999)
    return number


def get_test_name(midfix: str = ""):
    return f"TEST_{midfix}_{uuid.uuid4().hex}"
