# pylama:ignore=E501

import json
from json import JSONDecodeError
from typing import Union

import requests

from lemon_markets.common.errors import BaseError
from lemon_markets.settings import DEFAULT_REST_API_URL


class ApiResponseError(BaseError):

    def __init__(self, detail: str, status: int):
        try:
            self.status = status
            self.detail = json.loads(detail)
        except JSONDecodeError:
            self.detail = detail

    def to_representation(self):
        return "An error occurred while performing the request with error code {}: \n {}".format(self.status,
                                                                                                 str(self.detail))


class ApiResponse:
    content: dict = None
    status: int = 0
    _is_success: bool = True

    def __init__(self, content: Union[str, dict], status: int, is_success: bool, raise_error: bool = True):
        self.content = content
        self.status = status
        self._is_success = True
        if raise_error and not is_success:
            raise ApiResponseError(content, status)

    @property
    def successful(self):
        return self._is_success

    @property
    def has_errored(self):
        return not self._is_success


class ApiRequest:
    url: str
    method: str = "GET"
    body: dict
    authorization_token: str
    _account = None
    _kwargs: dict
    _response: ApiResponse

    def __init__(self, endpoint: str, method: str = "GET", body: dict = None,
                 authorization_token=None, url_params: dict = {}, **kwargs):
        if kwargs.get("account"):
            self._account = kwargs.get("account")
        if self._account and self._account.token:
            self.authorization_token = self._account.token
        if authorization_token:
            # do not double check with if above as this if should override the previous one
            self.authorization_token = str(authorization_token)

        self.url_params = url_params
        self._kwargs = kwargs
        self.method = method.lower()
        self.body = body
        self._build_url(endpoint)

        self._perform_request()

    def _build_url(self, endpoint: str):
        url = ""
        if not self._kwargs.get("ignore_account_url", False) and self._account:
            account_url = "accounts/{}/".format(self._account.uuid)
            url += account_url
        self.url = DEFAULT_REST_API_URL + url + endpoint

    def _perform_request(self):
        headers = {
            "Authorization": "Token {}".format(self.authorization_token)
        }
        try:
            if self.method == "post":
                response = requests.post(self.url, json=self.body, headers=headers, params=self.url_params)
            elif self.method == "delete":
                response = requests.delete(self.url, headers=headers, params=self.url_params)
            elif self.method == "patch":
                response = requests.patch(self.url, data=self.body, headers=headers, params=self.url_params)
            else:  # get
                response = requests.get(self.url, headers=headers, params=self.url_params)
            self._response = ApiResponse(content=response.content, status=response.status_code, is_success=response.ok)
        except Exception as e:
            raise e

    @property
    def response(self):
        if self._response.content:
            return json.loads(self._response.content)
        return self._response.content
