from http import HTTPStatus

from flask_restx import Namespace, Model, fields


def create_variable_columns_model(namespace: Namespace, name_snake_case: str) -> Model:
    """
    Creates a generic model for an entry with variable columns
    :param namespace:
    :param name:
    :return:
    """
    name_split = name_snake_case.split("_")
    name_camelcase = "".join([split[0].upper() + split[1:] for split in name_split])

    return namespace.model(
        name_camelcase,
        {
            "column_1": fields.String("Value for first column"),
            "column_2": fields.String("Value for second column"),
            "column_etc": fields.String("And so on..."),
        },
    )


def create_response_dictionary(
    success_message: str, success_model: Model = None
) -> dict:
    success_msg = "Success. " + success_message

    if success_model is not None:
        success_val = success_msg, success_model
    else:
        success_val = success_msg

    return {
        HTTPStatus.OK: success_val,
        HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error.",
        HTTPStatus.BAD_REQUEST: "Bad request. Missing or bad authentication or parameters",
        HTTPStatus.FORBIDDEN: "Unauthorized. Forbidden or invalid authentication.",
    }


def column_permissions_description(
    head_description: str,
    column_permissions_str_table: str,
    sub_description: str = "",
) -> str:
    """
    Creates a formatted description for column permissions
    :param head_description:
    :param sub_description:
    :param column_permissions_str_table:
    :return:
    """
    return f"""
    {head_description}

{sub_description}

## COLUMN PERMISSIONS    

{column_permissions_str_table}

    """
