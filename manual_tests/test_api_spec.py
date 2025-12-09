import json

from app import get_api_with_namespaces, create_flask_app


def test_api_spec():
    create_flask_app()
    api = get_api_with_namespaces()
    print(json.dumps(api.__schema__))
