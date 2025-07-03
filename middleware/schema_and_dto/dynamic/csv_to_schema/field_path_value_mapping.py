from dataclasses import dataclass

from middleware.schema_and_dto.enums import CSVColumnCondition


@dataclass
class FieldPathValueMapping:
    def __init__(
        self,
        field_path,
        field,
        name: str | CSVColumnCondition = CSVColumnCondition.SAME_AS_FIELD,
    ):
        self.field_path = field_path
        self.field = field
        if name == CSVColumnCondition.SAME_AS_FIELD:
            self.name = field_path[-1]
        else:
            self.name = name

    def get_schema_notation(self):
        return ".".join(self.field_path)

    def get_field_name(self):
        return self.field_path[-1]
