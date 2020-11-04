# pylama:ignore=E501

from typing import Union

from lemon_markets.common.helpers import UUIDObjectMixin
from lemon_markets.common.objects import AbstractApiObjectMixin, ListMixin, ListIterator
from lemon_markets.common.requests import ApiRequest


class AccountState:
    uuid: str
    _token: str
    _cash_to_invest: float = None
    _total_balance: float = None

    def fetch_account_state(self):
        request = ApiRequest(
            endpoint="accounts/{}/state/".format(self.uuid),
            method="GET",
            authorization_token=self._token
        )
        self._cash_to_invest = request.response.get("cash_to_invest")
        self._total_balance = request.response.get("total_balance")

    @property
    def cash_in_invest(self) -> float:
        if not self._cash_to_invest:
            self.fetch_account_state()
        return self._cash_to_invest

    @property
    def total_balance(self) -> float:
        if not self._total_balance:
            self.fetch_account_state()
        return self._total_balance


class Account(AccountState, UUIDObjectMixin, AbstractApiObjectMixin, ListMixin):
    _token: str

    class Fields(AbstractApiObjectMixin.Fields):
        name: str
        type: str
        currency: str
        uuid: str

    def __init__(self, uuid: str, authorization_token=None):
        super().__init__(uuid=uuid, authorization_token=authorization_token)
        self.uuid = uuid
        self._token = authorization_token

    @property
    def token(self) -> str:
        """
        An account can have multiple tokens. Thus, this makes calling the API way easier.
        :return: {str}
        """
        return self._token if self._token else None

    def retrieve(self):
        self.check_instance()
        request = ApiRequest(
            endpoint="accounts/{}/".format(self.uuid),
            method="GET",
            authorization_token=self._token
        )

        self.set_data(request.response)
        return self

    @staticmethod
    def list(authorization_token, limit: int = None, offset: int = None) -> ListIterator:
        return ListMixin.list(object_class=Account,
                              authorization_token=authorization_token,
                              limit=limit,
                              offset=offset
                              )
