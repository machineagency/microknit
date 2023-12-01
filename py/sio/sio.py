"""SocketIO transport."""
# Inspired by https://github.com/danni/uwebsockets/tree/esp8266/usocketio
# Heavily modified to use async websockets

import json
from .protocol import *
from .request import get
from ws import AsyncWebsocketClient
import usocket as socket
import uasyncio as a
import ussl


class LOGGER:
    @staticmethod
    def debug(s):
        if __debug__:
            print(s)

    def info(s):
        if __debug__:
            print(s)

    def warning(s):
        print(s)

    def error(s):
        print(s)

class SocketIOClient(AsyncWebsocketClient):
    """SocketIO transport."""

    def __init__(self, server, use_ssl=True, socket_delay_ms=5):
        AsyncWebsocketClient.__init__(self, socket_delay_ms)

        self._host = server
        self._ssl = use_ssl
        self._eio_connected = False
        self._sio_connected = False

        self._event_handlers = {}
        self._rxloop = None

    async def eio_connect(self):
        path = "socket.io/?EIO=4"
        headers, ret = await get(self._host, path, self._ssl, assert_code=200)
        packet_type, data = decode_packet(ret)
        assert packet_type == PACKET_OPEN ## EIO response
        data = json.loads(ret[1:]) ## EIO body

        path += '&sid=' + data['sid']
        LOGGER.debug(f"sid = {data['sid']}")

        LOGGER.debug("Setting up websocket connection...")
        ret = await self.handshake(f'{self._ssl and "wss" or "ws"}://{self._host}/{path}&transport=websocket')
        if ret:
            LOGGER.debug("Sending probe ping...")
            await self._send_packet(PACKET_PING, 'probe')
            packet_type, data = await self.recv()
            assert packet_type == PACKET_PONG and data == "probe"
            await self._send_packet(PACKET_UPGRADE)
            self._eio_connected = True
        else:
            LOGGER.error("Could not handshake websocket connection.")

    async def connect(self):
        if not self._eio_connected:
            LOGGER.debug("Connecting to engine.io...")
            await self.eio_connect()

        LOGGER.debug("Connecting to socket.io...")
        await self._send_message(MESSAGE_CONNECT)
        self._sio_connected = True
        self._rxloop = a.create_task(self.rxloop())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    async def close(self):
        if self._rxloop:
            await self._rxloop.close()
        AsyncWebsocketClient.close(self)

    async def emit(self, event, data):
        await self._send_message(MESSAGE_EVENT, (event, data))

    async def rxloop(self):
        while True:
            packet_type, data = await self.recv()
            await self._handle_packet(packet_type, data)

        LOGGER.debug("Exiting event loop")

    async def recv(self):
        line = await AsyncWebsocketClient.recv(self)
        return decode_packet(line)

    async def _handle_packet(self, packet_type, data):
        print("handle type:", packet_type)
        if packet_type is None:
            LOGGER.info("None")
            pass

        elif packet_type == PACKET_MESSAGE:
            LOGGER.info("Message")
            message_type, data = decode_packet(data)
            self._handle_message(message_type, data)

        elif packet_type == PACKET_CLOSE:
            LOGGER.info("Socket.io closed")
            self.close()

        elif packet_type == PACKET_PING:
            LOGGER.debug("< ping")
            await self._send_packet(PACKET_PONG, data)

        elif packet_type == PACKET_PONG:
            LOGGER.debug("< pong")

        elif packet_type == PACKET_NOOP:
            LOGGER.debug("noop")
            pass

        else:
            LOGGER.warning(f"Unhandled packet {packet_type}: {data}")

    def _handle_message(self, message_type, data):
        if message_type == MESSAGE_EVENT:
            event, data, sid = json.loads(data)
            self._handle_event(event, data, sid)

        elif message_type == MESSAGE_ERROR:
            LOGGER.error(f"Error: {data}")

        elif message_type == MESSAGE_DISCONNECT:
            LOGGER.info("Disconnected")
            self.close()

        else:
            LOGGER.warning(f"Unhandled message {message_type}: {data}")

    def _handle_event(self, event, data=None, sid=None):
        LOGGER.debug(f"Handling event '{event}' with data {data} from SID {sid}")
        for handler in self._event_handlers.get(event, []):
            LOGGER.debug(f"Calling handler {handler}")
            a.create_task(handler(data, sid))

    async def _send_packet(self, packet_type, data=''):
        await self.send('{}{}'.format(packet_type, data))

    async def _send_message(self, message_type, data=None):
        await self._send_packet(PACKET_MESSAGE, '{}{}'.format(message_type, json.dumps(data)))

    async def ping(self):
        LOGGER.debug("> ping")
        await self._send_packet(PACKET_PING)

    def on(self, event):
        """Register an event handler with the socket."""
        def inner(func):
            LOGGER.debug(f"Registered {func} to handle {event}")
            self._event_handlers.setdefault(event, []).append(func)
        return inner

if __name__ == "__main__":
    from ablink import blink_loop

    host = "esphub.mehtank.com"
    sio = SocketIOClient(host)

    async def main():
        tasks = [blink_loop(debug=True), sio.rxloop()]
        await a.gather(*tasks)

    a.run(main())
