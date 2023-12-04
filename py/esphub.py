import network
import uasyncio as a
from ubinascii import hexlify

from .ablink import blink
from .sio import SocketIOClient


class ESPHub(SocketIOClient):

    def __init__(self, server, use_ssl=True, socket_delay_ms=5, led_pin=2):
        print("Create SocketIO instance...")
        SocketIOClient.__init__(self, server, use_ssl, socket_delay_ms=socket_delay_ms)
        print("Created.")
        self.led_pin = led_pin

    async def connect(self):
        await SocketIOClient.connect(self)
        wifi = network.WLAN()
        print("Registering on ESPHub...")
        await self.emit("register", dict(name= "mpy",
                                        mac = hexlify(wifi.config('mac'), ':').decode().upper(),
                                        ip  = wifi.ifconfig()[0],
                                       ))

        # Socket IO on event... this is also how you make more events
        @self.on("blink")
        async def dblblink(data, sid):
            await blink(50,50,pin=self.led_pin)
            await blink(50,50,pin=self.led_pin)

    def command(self, event, who, data=None):
        for sid in who:
            data=dict(sid=sid, event=event, data=data)
            a.create_task(self.emit('command',data))
            print(f"Emitting data {data}")

    def __getattr__(self, fn):
        return lambda *args, **kwargs: self.command(fn, *args, **kwargs)
