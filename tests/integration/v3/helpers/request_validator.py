from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel
from starlette.testclient import TestClient


class RequestValidatorFastAPI:

    def __init__(self, client: TestClient):
        self.client = client

    def open_v3(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        expected_model: type[BaseModel] | None = None,
        **kwargs
    ) -> BaseModel | dict:
        if params:
            kwargs['params'] = params

        response = self.client.request(
            method=method,
            url=url,
            headers={"Authorization": "Bearer token"},  # Fake authentication that is overridden during testing
            **kwargs
        )
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
        json = response.json()

        if expected_model:
            return expected_model(**json)
        return json

    def get_v3(
        self,
        url: str,
        params: dict | None = None,
        expected_model: type[BaseModel] | None = None,
        **kwargs
    ) -> BaseModel | dict:
        return self.open_v3(
            method="GET",
            url=url,
            params=params,
            expected_model=expected_model,
            **kwargs
        )

    def post_v3(
        self,
        url: str,
        params: dict | None = None,
        expected_model: type[BaseModel] | None = None,
        **kwargs
    ) -> BaseModel | dict:
        return self.open_v3(
            method="POST",
            url=url,
            params=params,
            expected_model=expected_model,
            **kwargs
        )

    def put_v3(
        self,
        url: str,
        params: dict | None = None,
        expected_model: type[BaseModel] | None = None,
        **kwargs
    ) -> BaseModel | dict:
        return self.open_v3(
            method="PUT",
            url=url,
            params=params,
            expected_model=expected_model,
            **kwargs
        )

    def delete_v3(
        self,
        url: str,
        params: dict | None = None,
        expected_model: type[BaseModel] | None = None,
        **kwargs
    ) -> BaseModel | dict:
        return self.open_v3(
            method="DELETE",
            url=url,
            params=params,
            expected_model=expected_model,
            **kwargs
        )
