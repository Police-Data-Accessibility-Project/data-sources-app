from enum import Enum
from http import HTTPStatus
from typing import Any, Generator

from pydantic import BaseModel


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


ALL_METHODS_STR = ["get", "post", "put", "delete", "patch"]
ALL_METHODS_ENUM = [
    HTTPMethod.GET,
    HTTPMethod.POST,
    HTTPMethod.PUT,
    HTTPMethod.DELETE,
    HTTPMethod.PATCH,
]


class MethodInfo(BaseModel):
    parent_path: "PathInfo"
    method: HTTPMethod
    content: dict

    def get_response_codes(self):
        for key, value in self.content["responses"].items():
            yield HTTPStatus(int(key))

    def has_response(self, response_code: HTTPStatus):
        response_codes = list(self.get_response_codes())
        return response_code in response_codes

    def has_any_authorization_header(self):
        if "parameters" not in self.content:
            return False
        parameters = self.content["parameters"]
        for parameter in parameters:
            if parameter["in"] == "header" and parameter["name"] == "Authorization":
                return True
        return False

    def has_authorization_header(self, header_name: str):
        if "parameters" not in self.content:
            return False
        parameters = self.content["parameters"]
        for parameter in parameters:
            if parameter["in"] != "header":
                continue
            if parameter["name"] != "Authorization":
                continue
            if header_name in parameter["default"]:
                return True
        return False

    def pathname(self) -> str:
        return self.parent_path.route_name

    def __str__(self):
        return f"{self.method.name} {self.pathname()}"


class PathInfo(BaseModel):
    route_name: str
    content: dict

    def get_allowed_method_info(self) -> Generator[MethodInfo, Any, None]:
        for key, value in self.content.items():
            if key not in ALL_METHODS_STR:
                continue
            method = HTTPMethod(key)
            content = value
            yield MethodInfo(method=method, content=content, parent_path=self)

    def get_allowed_methods(self) -> Generator[HTTPMethod, Any, None]:
        for key, value in self.content.items():
            if key not in ALL_METHODS_STR:
                continue
            method = HTTPMethod(key)
            yield method

    def get_disallowed_methods(self) -> Generator[HTTPMethod, Any, None]:
        allowed_methods = list(self.get_allowed_methods())
        for method in ALL_METHODS_ENUM:
            if method not in allowed_methods:
                yield method


class SpecManager:

    def __init__(self, spec: dict):
        self.spec = spec

    def get_paths(self):
        for pathname, pathdict in self.spec["paths"].items():
            yield PathInfo(route_name=pathname, content=pathdict)

    def get_methods_with_response(
        self, response_status: HTTPStatus
    ) -> Generator[MethodInfo, Any, None]:
        for path_info in self.get_paths():
            for method_info in path_info.get_allowed_method_info():
                if method_info.has_response(response_status):
                    yield method_info

    def get_methods_with_any_header(self) -> Generator[MethodInfo, Any, None]:
        for path_info in self.get_paths():
            for method_info in path_info.get_allowed_method_info():
                if method_info.has_any_authorization_header():
                    yield method_info

    def get_methods_with_specific_header(
        self, header_name: str
    ) -> Generator[MethodInfo, Any, None]:
        for path_info in self.get_paths():
            for method_info in path_info.get_allowed_method_info():
                if method_info.has_authorization_header(header_name):
                    yield method_info
