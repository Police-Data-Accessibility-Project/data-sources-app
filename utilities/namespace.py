from flask_restx import Namespace

def create_namespace() -> Namespace:
    """
    Create a default namespace to be used with Flask_restx resources.
    Each namespace can contain the route definitions and other documentation about the resource
    which can then be imported into the API in the create_app function.
    :return:
    """

    namespace = Namespace("/", description="Default Namespace")

    return namespace