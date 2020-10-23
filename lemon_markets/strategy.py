from lemon_markets.account import Account
from lemon_markets.common.helpers import UUIDAccountObjectMixin
from lemon_markets.common.objects import AbstractApiObjectMixin, ListMixin, ListIterator
from lemon_markets.common.requests import ApiRequest


class Strategy(UUIDAccountObjectMixin, AbstractApiObjectMixin, ListMixin):
    _list_endpoint = "strategies/"

    class Fields(AbstractApiObjectMixin.Fields):
        account: Account
        name: str
        description: str
        uuid: str
        is_private: bool

    def __init__(self,
                 uuid: str,
                 account: Account = None,
                 **kwargs,
                 ):
        super().__init__(uuid=uuid, account=account, **kwargs)

    def retrieve(self):
        self.check_instance()
        request = ApiRequest(
            endpoint="strategies/{}/".format(self.uuid),
            account=self.account,
            method="GET"
        )

        self.set_data(request.response)
        return self

    @staticmethod
    def list(account: Account, limit: int = None, offset: int = None) -> ListIterator:
        return ListMixin.list(object_class=Strategy, account=account, limit=limit, offset=offset,
                              list_endpoint="strategies/")
