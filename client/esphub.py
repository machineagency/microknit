from socketio import Client
from socketio.exceptions import BadNamespaceError
from pprint import pformat, pprint
from zenlog import log as logging
import time


DELAY = 0.1

class ESPHub(Client):
    def __init__(self, fakeesp=False, url = "https://esphub.mehtank.com", **kwargs):
        logging.debug(f"Initializing ESPHub object at {url}")
        Client.__init__(self)

        self._fakeesp = fakeesp
        self._url = url
        self._kwargs = kwargs

        self._filter = ""
        self._clients = dict()
        self._register()
        self._reconnect()

        self._esps = []

    @property
    def esps(self):
        return self._esps

    @esps.setter
    def clients(self, members):
        self._esps = members

    @property
    def clients(self):
        return self._clients

    @clients.setter
    def clients(self, members):
        self._clients = members


    def _reconnect(self):
        logging.debug(f"Connecting...")
        self.connect(self._url, **self._kwargs)
        time.sleep(DELAY)
        if not self._fakeesp:
            self.emit("enter", "membership")
            self.refresh()

    def _register(self):
        @self.event
        def disconnect():
            logging.info("Disconnected from esphub server!")

        @self.event
        def connect():
            logging.info("Connected to esphub server!")

        @self.on("list")
        def ls(data):
            logging.debug("Got new client list:")
            self.clients = data
            logging.debug(pformat(data))
            self.filter(*self._filter)

        @self.event
        def joined(data):
            logging.debug('user(s) joined:', data)
            self.clients.update(data)
            logging.debug(pformat(self.clients))
            self.filter(*self._filter)

        @self.event
        def left(data):
            logging.debug('user(s) left:', data)
            for k in data.keys():
                self.clients.pop(k, None)
            logging.debug(pformat(self.clients))
            self.filter(*self._filter)

        @self.on("server-ack")
        def ack(data):
            logging.debug(f"Server acknowledged packet {pformat(data)}!")

        @self.on("*")
        def catchall(event, data, sid=None):
            logging.debug(f"Got unhandled event {event} from client {sid}!")
            logging.debug(pformat(data))

    def emit(self, *args, **kwargs):
        logging.debug(f"Emitting {args}")
        try:
            Client.emit(self, *args, **kwargs)
        except BadNamespaceError:
            logging.warning("Not connected!, could not send!")
        time.sleep(DELAY)

    def refresh(self):
        self.emit("list")

    def filter(self, filt='', count=0):
        # Create an ordered list of all ESPHub clients that match filt, in any of:
        # - client ID
        # - client name
        # - client mac address
        # - client IP address
        # in that order, first prioritizing exact matches, then substring matches
        # up to at most count matches; all matches for count=0

        self._filter = filt, count
        self._esps = []
        if not filt:
            return self._esps

        fns = (
            lambda k, v: k,
            lambda k, v: v["name"],
            lambda k, v: "%08x" % v["mac"],
            lambda k, v: v["ip"],
        )
        tests = (
            lambda a1, a2: a1 == a2,
            lambda a1, a2: a1 in a2,
        )

        for test in tests:
            for fn in fns:
                for k, v in self.clients.items():
                    if test(filt, fn(k, v)) and k not in self._esps:
                        self._esps.append(k)
                        count -= 1
                        if count == 0:
                            return self._esps
                            
        return self._esps

    def find(self, filt=''):
        # return the highest priority ESPHub client according to filter priority
        return self.filter(filt, count=1)

    def command(self, event, data=None, broadcast=False, who=''):
        tosend = []
        if who and who in self._clients:
            tosend = [who]
        elif self._esps:
            tosend = self._esps
        elif broadcast:
            tosend = self._clients.keys()

        if not tosend:
            logging.warning(f"No clients found (did you forget to filter() first?)")
            return

        for who in tosend:
            if who in self._clients:
                logging.debug(f"Sending command to {who}: event = {event}")
                self.emit("command", dict(sid=who, event=event, data=data))
            else:
                logging.warning(f"Client {who} not found")

    def __getattr__(self, fn):
        return lambda *args, **kwargs: self.command(fn, *args, **kwargs)

    def __del__(self):
        self.disconnect()
