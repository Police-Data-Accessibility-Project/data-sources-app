from typing import Any, Dict


def update_if_not_none(dict_to_update: Dict[str, Any], secondary_dict: Dict[str, Any]):
    for key, value in secondary_dict.items():
        if value is not None:
            dict_to_update[key] = value
