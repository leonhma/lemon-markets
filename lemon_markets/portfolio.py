from lemon_markets.account import Account
from lemon_markets.common.objects import AbstractApiObjectMixin, ListMixin, ListIterator
from lemon_markets.common.requests import ApiRequest
from lemon_markets.instrument import Instrument


class Portfolio(AbstractApiObjectMixin, ListMixin):

    class Fields(AbstractApiObjectMixin.Fields):
        account: Account
        quantity: int
        average_price: float
        instrument: Instrument
        uuid: str

    def __init__(self,
                 account: Account,
                 isin: str = None,
                 **kwargs):
        super().__init__(isin=isin, account=account, **kwargs)
        self.account = account
        self.isin = isin

    @property
    def retrieve(self):
        request = ApiRequest(
            endpoint="portfolio/{}/".format(self.isin),
            account=self.account,
            method="GET"
        )

        self.set_data(request.response)
        return self

    @staticmethod
    def list(account: Account, limit: int = None, offset: int = None) -> ListIterator:
        return ListMixin.list(object_class=Portfolio, account=account, limit=limit, offset=offset,
                              list_endpoint="portfolio/")


class AggregatedPortfolio(AbstractApiObjectMixin, ListMixin):

    class Fields(AbstractApiObjectMixin.Fields):
        account: Account
        quantity: int
        average_price: float
        instrument: Instrument
        uuid: str

    def __init__(self,
                 account: Account,
                 isin: str = None,
                 **kwargs
                 ):
        super().__init__(isin=isin, account=account, **kwargs)
        self.account = account
        self.isin = isin

    @property
    def retrieve(self):
        request = ApiRequest(
            endpoint="portfolio/{}/aggregated/".format(self.isin),
            account=self.account,
            method="GET"
        )

        self.set_data(request.response)
        return self

    @staticmethod
    def list(account: Account, limit: int = None, offset: int = None) -> ListIterator:
        return ListMixin.list(object_class=Portfolio, account=account, limit=limit, offset=offset,
                              list_endpoint="portfolio/aggregated/")
