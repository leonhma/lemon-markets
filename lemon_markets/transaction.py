# pylama:ignore=E501

from lemon_markets.account import Account
from lemon_markets.common.helpers import UUIDAccountObjectMixin
from lemon_markets.common.objects import AbstractApiObjectMixin, ListMixin
from lemon_markets.common.requests import ApiRequest
from lemon_markets.order import Order


class Transaction(UUIDAccountObjectMixin, AbstractApiObjectMixin, ListMixin):

    class Fields(AbstractApiObjectMixin.Fields):
        account: Account
        name: str
        description: str
        uuid: str
        is_private: bool
        related_order: Order

    def __init__(self,
                 account: Account,
                 uuid: str, **kwargs):
        super().__init__(uuid=uuid, account=account, **kwargs)

    def retrieve(self):
        self.check_instance()
        request = ApiRequest(
            endpoint="transactions/{}/".format(self.uuid),
            account=self.account,
            method="GET"
        )

        self.set_data(request.response)
        return self

    @staticmethod
    def list(account: Account, limit: int = None, offset: int = None):
        return ListMixin.list(object_class=Transaction, account=account, limit=limit, offset=offset,
                              list_endpoint="transactions/")
