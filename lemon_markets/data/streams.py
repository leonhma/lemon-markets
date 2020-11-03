# pylama:ignore=E501

import json
from multiprocessing import Manager, Process, Value
from time import time
from typing import Callable

from websocket import create_connection

from lemon_markets.common.errors import StreamError
from lemon_markets.settings import DEFAULT_STREAM_API_URL


class BaseSerializer:
    json_content: dict

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
    time: float
    bid_quantity: int
    ask_quantity: int

    def __init__(self, message: str):
        super().__init__(message)
        self.isin = self.json_content.get("isin")
        self.bid_price = self.json_content.get("bid_price")
        self.ask_price = self.json_content.get("ask_price")
        self.time = float(self.json_content.get("date"))
        self.bid_quantity = self.json_content.get("bid_quan")
        self.ask_quantity = self.json_content.get("ask_quan")


class Tick(BaseSerializer):
    isin: str
    quantity: int
    price: float
    time: float
    side: str

    def __init__(self, message: str):
        super().__init__(message)
        self.isin = self.json_content.get("isin")
        self.price = self.json_content.get("price")
        self.quantity = self.json_content.get("quantity")
        self.time = float(self.json_content.get("date"))
        self.side = self.json_content.get("side")


class WSWorker(Process):
    _last_message_time = 0

    def __init__(self, keepalive, restart, subscribed, serializer,
                 connect_url, typ3, callback, timeout, frequency_limit):
        super().__init__(target=self)
        self._keepalive = keepalive
        self._restart = restart
        self._subscribed = subscribed
        self._serializer = serializer
        self._connect_url = connect_url
        self._type = typ3
        self._callback = callback
        self._timeout = timeout
        self._frequency_limit = frequency_limit

    def run(self):
        self._restart.value = False
        while self._keepalive.value:
            ws = create_connection(self._connect_url,
                                   self._timeout)
            for each in self._subscribed.keys():
                ws.send(json.dumps({
                                  "action": "subscribe",
                                  "type": self._type,
                                  "specifier": self._subscribed[each],
                                  "value": each
                              }))
            while self._keepalive.value and not self._restart.value:
                if(time() - self._last_message_time > self._frequency_limit):
                    continue
                serialized = self._serializer_class(ws.recv(), self._subscribed)
                try:
                    self._callback(serialized)
                except Exception as e:
                    self.__del__()
                    raise ValueError(f'Error with '
                                     'callback function '
                                     f'{self._callback}: '
                                     f'{e.__class__.__name__}!')

                self._last_message_time = time()
            ws.close()


class StreamBase():
    _serializer = _connect_url = _type = _specifiers = _default_specifier = None

    _subscribed = Manager().dict()
    _keepalive = Value('B', True)
    _restart = Value('B', False)

    def __init__(self, callback: Callable, timeout: float, frequency_limit: float):
        self._callback = callback
        self._timeout = timeout
        self._frequency_limit = frequency_limit

    def __del__(self):
        self.stop()

    def subscribe(self, isin: str, specifier: str = None):
        if specifier is None:
            specifier = self._default_specifier
        assert specifier in self._specifiers
        if isin in self._subscribed.keys():
            return
        self._subscribed[isin] = specifier
        self._restart.value = True

    def unsubscribe(self, isin: str):
        del self._subscribed[isin]
        self._restart.value = True

    def start(self, daemon: bool = True):
        self._ws_process = WSWorker(self._keepalive, self._restart,
                                    self._subscribed, self._serializer,
                                    self._connect_url, self._type,
                                    self._callback, self._timeout,
                                    self._frequency_limit)
        self._ws_process.daemon = daemon
        self._ws_process.start()
        self._keepalive.value = True

    def stop(self):
        try:
            self._keepalive.value = False
            self._ws_process.join()
        except Exception:
            pass


class TickStream(StreamBase):
    _connect_url = DEFAULT_STREAM_API_URL+'marketdata/'
    _type = 'trades'
    _serializer_class = Tick
    _specifiers = ['with-quantity', 'with-uncovered', 'with-quantity-with-uncovered']
    _default_specifier = 'with-uncovered'


class QuoteStream(StreamBase):
    _connect_url = DEFAULT_STREAM_API_URL+'quotes/'
    _type = 'quotes'
    _serializer_class = Quote
    _specifiers = ['with-quantity', 'with-price', 'with-quantity-with-price']
    _default_specifier = 'with-price'
