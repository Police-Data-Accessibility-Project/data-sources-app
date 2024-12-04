from enum import Enum


class RestxModelPlaceholder(Enum):
    # Placeholders for nested models
    VARIABLE_COLUMNS = "variable_columns"
    LIST_VARIABLE_COLUMNS = "list_variable_columns"


class CSVColumnCondition(Enum):
    """
    SAME_AS_FIELD: Indicates that the csv column
    should be the same as the field in the schema
    """
    SAME_AS_FIELD = "SAME_AS_FIELD"
