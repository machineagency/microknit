import network
from ubinascii import hexlify

from .ablink import blink
from .sio import SocketIOClient


async def esphub(server, use_ssl=True, socket_delay_ms=5, led_pin=2):
    print("Create SocketIO instance...")
    sio = SocketIOClient(server, use_ssl, socket_delay_ms=socket_delay_ms)
    print("Created...")
    await sio.connect()
    print("Connected...")

    wifi = network.WLAN()
    await sio.emit("register", dict(name= "mpy",
                                    mac = hexlify(wifi.config('mac'), ':').decode().upper(),
                                    ip  = wifi.ifconfig()[0],
                                   ))

    @sio.on("blink")
    async def dblblink(data, sid):
        await blink(50,50,pin=led_pin)
        await blink(50,50,pin=led_pin)
    
    return sio
