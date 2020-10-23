import datetime
import json
from typing import Callable, Type, Union

import websocket

from lemon_markets.common.errors import StreamError
from lemon_markets.settings import DEFAULT_STREAM_API_URL


class BaseSerializer:
    json_content: dict = None

    def __init__(self, message: str):
        self.json_content = json.loads(message)
        self.__check_for_error()

    def __check_for_error(self):
        if self.json_content.get("error"):
            raise StreamError(detail=self.json_content.get("message"))

        if not self.json_content:
            raise StreamError(detail="Unknown error")

    def to_representation(self):
        output_dict: dict = {}
        for key, value in self.__dict__.items():
            if value and key != "json_content":
                output_dict[key] = value
        return output_dict

    def __repr__(self):
        output = self.to_representation()
        return str(self.__class__.__name__) \
               + "(" + ", ".join(["{}={}".format(key, value) for key, value in output.items()]) \
               + ")"


class Quote(BaseSerializer):
    isin: str
    bid_price: float
    ask_price: float
    date: datetime.datetime
    bid_quantity: int
    ask_quantity: int

    def __init__(self, message: str):
        super().__init__(message)
        self.isin = self.json_content.get("isin")
        self.bid_price = self.json_content.get("bid_price")
        self.ask_price = self.json_content.get("ask_price")
        self.date = datetime.datetime.fromtimestamp(float(self.json_content.get("date")))
        self.bid_quantity = self.json_content.get("bid_quan")
        self.ask_quantity = self.json_content.get("ask_quan")


class Tick(BaseSerializer):
    isin: str
    quantity: int
    price: float
    date: datetime.datetime
    side: str

    def __init__(self, message: str):
        super().__init__(message)
        self.isin = self.json_content.get("isin")
        self.price = self.json_content.get("price")
        self.quantity = self.json_content.get("quantity")
        self.date = datetime.datetime.fromtimestamp(float(self.json_content.get("date")))
        self.side = self.json_content.get("side")


class WebsocketBase:
    serializer_class: Type[BaseSerializer] = None
    url: str = DEFAULT_STREAM_API_URL
    on_message: Callable = None
    on_open: Callable = None
    on_close: Callable = None
    on_error: Callable = None
    __open_status: bool = False
    _ws: websocket.WebSocketApp = None

    def __init__(self, on_message, on_open: Callable = None, on_close: Callable = None, on_error: Callable = None):
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_error = on_error
        self._ws = websocket.WebSocketApp(
            url=self.url,
            on_message=lambda ws, msg: self.__on_message(ws, msg),
            on_error=lambda ws, msg: self.__on_error(ws, msg),
            on_close=lambda ws: self.__on_close(ws),
            on_open=lambda ws: self.__on_open(ws)
        )

    def __on_message(self, ws, message):
        if self.on_message:
            instance = self.serializer_class(message=message)
            self.on_message(ws, instance)

    def __on_open(self, ws):
        if self.on_open:
            self.on_open(ws)

    def __on_error(self, ws, msg):
        if self.on_error:
            self.on_error(ws, msg)

    def __on_close(self, ws):
        self.is_open = False
        if self.on_close:
            self.on_close(ws)

    def run(self):
        return self._ws.run_forever()

    def subscribe(self, **kwargs):
        if not kwargs:
            raise NotImplementedError()
        else:
            self._ws.send(kwargs)

    def unsubscribe(self, isin: Union[str, "Instrument"]):
        self._ws.send(json.dumps({
            "value": str(isin),
            "action": "unsubscribe"
        }))

    def close(self):
        self.is_open = False
        self._ws.close()

    @property
    def is_open(self) -> bool:
        return self.__open_status

    @is_open.setter
    def is_open(self, value: bool):
        self.__open_status = value

    @is_open.deleter
    def is_open(self):
        self.__open_status = False


class QuoteStream(WebsocketBase):
    url = DEFAULT_STREAM_API_URL + "quotes/"
    serializer_class = Quote

    def subscribe(self, isin: Union[str, "Instrument"], specifier: str = "with-quantity-with-prices"):
        self._ws.send(json.dumps(
            {
                "value": str(isin),
                "type": "quotes",
                "action": "subscribe",
                "specifier": specifier
            }
        ))


class TickStream(WebsocketBase):
    url = DEFAULT_STREAM_API_URL + "marketdata/"
    serializer_class = Tick

    def subscribe(self, isin: Union[str, "Instrument"], specifier: str = "with-uncovered"):
        self._ws.send(json.dumps(
            {
                "value": str(isin),
                "type": "trades",
                "action": "subscribe",
                "specifier": specifier
            }
        ))
