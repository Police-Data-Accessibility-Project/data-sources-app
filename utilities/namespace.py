from flask_restx import Namespace
from enum import Enum
from collections import namedtuple

NamespaceAttributes = namedtuple("NamespaceAttributes", ["path", "description"])


class AppNamespaces(Enum):
    DEFAULT = NamespaceAttributes(path="/", description="Default Namespace")
    SEARCH = NamespaceAttributes(path="search", description="Search Namespace")
    AUTH = NamespaceAttributes(path="auth", description="Authentication Namespace")
    OAUTH = NamespaceAttributes(path="oauth", description="OAuth Namespace")
    PERMISSIONS = NamespaceAttributes(
        path="permissions", description="Permissions Namespace"
    )
    DEV = NamespaceAttributes(path="dev", description="Developer Namespace")
    DATA_REQUESTS = NamespaceAttributes(
        path="data-requests", description="Data Requests Namespace"
    )
    AGENCIES = NamespaceAttributes(path="agencies", description="Agencies Namespace")
    DATA_SOURCES = NamespaceAttributes(
        path="data-sources", description="Data Sources Namespace"
    )
    TYPEAHEAD = NamespaceAttributes(path="typeahead", description="Typeahead Namespace")
    CHECK = NamespaceAttributes(path="check", description="Check Namespace")
    USER = NamespaceAttributes(path="user", description="User Profile Namespace")
    GITHUB = NamespaceAttributes(path="github", description="Github Namespace")
    NOTIFICATIONS = NamespaceAttributes(
        path="notifications", description="Notifications Namespace"
    )
    MAP = NamespaceAttributes(path="map", description="Map Namespace")
    BULK = NamespaceAttributes(path="bulk", description="Bulk Namespace")
    MATCH = NamespaceAttributes(path="match", description="Match Namespace")
    LOCATIONS = NamespaceAttributes(path="locations", description="Locations Namespace")
    METRICS = NamespaceAttributes(path="metrics", description="Metrics Namespace")
    ADMIN = NamespaceAttributes(path="admin", description="Admin Namespace")
    CONTACT = NamespaceAttributes(path="contact", description="Contact Namespace")
    METADATA = NamespaceAttributes(path="metadata", description="Metadata Namespace")


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
