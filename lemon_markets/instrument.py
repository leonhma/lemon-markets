# pylama:ignore=E501

from typing import Union

from lemon_markets.common.objects import AbstractApiObjectMixin, ListMixin, ListIterator
from lemon_markets.common.requests import ApiRequest


class Instrument(AbstractApiObjectMixin, ListMixin):
    _list_endpoint = "data/instruments/"

    class Fields(AbstractApiObjectMixin.Fields):
        title: str
        type: str
        isin: str
        wkn: str

    def __init__(self, isin: str = None,
                 account=None,
                 authorization_token=None,
                 **kwargs):
        super().__init__(isin=isin, authorization_token=authorization_token, account=account, **kwargs)
        self.isin = isin
        self.account = account
        self.authorization_token = authorization_token

    def to_representation(self) -> str:
        if hasattr(self, "isin"):
            return self.isin
        return ""

    @staticmethod
    def list(
            search: str = "",
            type: Union[str, list] = "",
            authorization_token=None,
    ) -> ListIterator:
        return ListMixin.list(object_class=Instrument,
                              search=search,
                              type=type,
                              authorization_token=authorization_token)

    def retrieve(self):
        request = ApiRequest(
            endpoint="data/instruments/{}/".format(self.isin),
            method="GET",
            authorization_token=self.authorization_token,
            account=self.account
        )

        self.set_data(request.response)
        return self
