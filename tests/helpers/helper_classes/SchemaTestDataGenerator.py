from datetime import datetime
from typing import Optional

from marshmallow import Schema, fields
from marshmallow.fields import Field

from middleware.constants import DATE_FORMAT
from tests.helpers.common_test_data import (
    get_random_number_for_testing,
    get_random_boolean,
    get_random_possible_enum_value,
    get_test_name,
)


class SchemaTestDataGenerator:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.fields = schema.fields
        self.output: dict = {}

    def generate(self):
        for key, field in self.fields.items():
            try:
                self.output[key] = self.generate_test_data(field)
            except NotImplementedError as e:
                raise NotImplementedError(f"Field {key} is not supported: {e}")
        return self.output

    def generate_test_data(self, field: Field):
        if isinstance(field, fields.String):
            return get_test_name()
        elif isinstance(field, fields.Number):
            return get_random_number_for_testing()
        elif isinstance(field, fields.Boolean):
            return get_random_boolean()
        elif isinstance(field, fields.Enum):
            return get_random_possible_enum_value(field.enum)
        elif isinstance(field, fields.Date):
            return datetime.now().strftime(DATE_FORMAT)
        elif isinstance(field, fields.List):
            inner_field = field.inner
            return [self.generate_test_data(inner_field) for _ in range(5)]
        else:
            raise NotImplementedError(f"Field type {type(field)} is not supported")


def generate_test_data_from_schema(
    schema: Schema, override: Optional[dict] = None
) -> dict:
    """
    Generates a dictionary of test data based on
    the provided schema
    :param schema:
    :return:
    """
    result = SchemaTestDataGenerator(schema).generate()
    if override is not None:
        result.update(override)
    return result
