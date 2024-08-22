from flask_restx import Namespace
from enum import Enum
from collections import namedtuple

NamespaceAttributes = namedtuple("NamespaceAttributes", ["path", "description"])


class AppNamespaces(Enum):
    DEFAULT = NamespaceAttributes(path="/", description="Default Namespace")
    SEARCH = NamespaceAttributes(path="search", description="Search Namespace")
    AUTH = NamespaceAttributes(path="auth", description="Authentication Namespace")
    DEV = NamespaceAttributes(path="dev", description="Developer Namespace")


def create_namespace(
    namespace_attributes: AppNamespaces = AppNamespaces.DEFAULT,
) -> Namespace:
    """
    Create a namespace to be used with Flask_restx resources.
    Each namespace can contain the route definitions and other documentation about the resource
    which can then be imported into the API in the create_app function.
    :return:
    """

    path = namespace_attributes.value.path
    description = namespace_attributes.value.description
    namespace = Namespace(path, description=description)

    return namespace
