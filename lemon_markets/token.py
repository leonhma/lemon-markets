from typing import List, Union
from lemon_markets.account import Account
from lemon_markets.common.objects import AbstractApiObjectMixin, ListIterator, ListMixin
from lemon_markets.common.requests import ApiRequest
from lemon_markets.strategy import Strategy


class Permission(AbstractApiObjectMixin):

    class Fields(AbstractApiObjectMixin.Fields):
        name: str
        has_permission: bool
        total_limit: float


class Token(AbstractApiObjectMixin):
    key: str

    def __init__(self, key: str, retrieve: bool = True):
        super().__init__(key=key)
        if retrieve:
            self.retrieve()

    class Fields(AbstractApiObjectMixin.Fields):
        account: Account
        strategy: Strategy
        key: str
        name: str
        permissions: List[Permission]

    def retrieve(self):
        request = ApiRequest(
            endpoint="token/{}/".format(self.key),
            authorization_token=self.key,
            method="GET",
        )

        self._build_object(request=request)
        # make the usage of the Account class object more convenient by accessing the token directly
        if hasattr(self, "account"):
            self.account._token = self.key

        return self

    @staticmethod
    def list(authorization_token: Union[str, "Token"] = None) -> ListIterator:
        return ListMixin.list(object_class=Token,
                              authorization_token=authorization_token,
                              list_endpoint="token/")

    def __str__(self):
        return str(self.key)
