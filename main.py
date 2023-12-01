import json
import uasyncio as a

from py.wifi import connect
from py.esphub import esphub
from py.silversend import Silversend


with open("config.json") as f:
    config = json.load(f)
wificonf = config["wifi"]
esphubconf = config["esphub"]

async def main():
    wifi = await connect(**wificonf)
    hub = await esphub(**esphubconf, led_pin=config["led_pin"])

    s = Silversend(-20, 20)

    pattern = [False, True, False, False] * 10
    s.load(pattern)

    print("we can do things and we're starting")
    while True:
        try:
            s.update()
            await a.sleep(0)
        except KeyboardInterrupt:
            print("Received exit, exiting")
            hub.close()

a.run(main())
