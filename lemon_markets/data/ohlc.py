# pylama:ignore=E501

import datetime
from typing import Union

from lemon_markets.common.objects import AbstractApiObject, ListMixin
from lemon_markets.common.requests import ApiRequest


class OHLCObject(AbstractApiObject):
    class Fields(AbstractApiObject.Fields):
        open: float
        high: float
        low: float
        close: float
        date: datetime.datetime


class TradeObject(AbstractApiObject):
    class Fields(AbstractApiObject.Fields):
        date: datetime.datetime
        price: float


class AbstractDataMixin(ListMixin):

    @classmethod
    def _build_endpoint(cls, instrument) -> str:
        raise NotImplementedError()

    def latest(self, instrument, authorization_token=None):
        request = ApiRequest(
            endpoint=self._build_endpoint(instrument=instrument) + "latest/",
            method="GET",
            authorization_token=authorization_token
        )

        self.set_data(request.response)
        return self

    def retrieve(self, instrument, authorization_token=None):
        return self.latest(instrument=instrument, authorization_token=authorization_token)

    @classmethod
    def list(
             cls,
             instrument,
             ordering: str = "-date",
             date_from: Union[str, datetime.datetime] = None,
             date_until: Union[str, datetime.datetime] = None,
             limit: int = None,
             offset: int = None,
             authorization_token=None,
             ):
        return ListMixin.list(ordering=ordering,
                              date_from=date_from,
                              date_until=date_until,
                              limit=limit,
                              offset=offset,
                              authorization_token=authorization_token,
                              list_endpoint=cls._build_endpoint(instrument=instrument),
                              object_class=cls)


class M1(OHLCObject, AbstractDataMixin):

    @classmethod
    def _build_endpoint(cls, instrument) -> str:
        endpoint = "data/instruments/{}/candle/m1/".format(str(instrument))
        return endpoint


class Trades(TradeObject, AbstractDataMixin):

    @classmethod
    def _build_endpoint(cls, instrument) -> str:
        endpoint = "data/instruments/{}/ticks/".format(str(instrument))
        return endpoint


class Ticks(Trades):
    """
    Ticks and trades are the same. Just added this class in order to give you guys both possibilities:)
    """
    pass
