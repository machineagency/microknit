import json
import uasyncio as a

from py.wifi import connect
from py.esphub import ESPHub
from py.silversend import Silversend

sids = []



with open("config.json") as f:
    config = json.load(f)
wificonf = config["wifi"]
esphubconf = config["esphub"]

async def main():
    wifi = await connect(**wificonf)
    hub = ESPHub(**esphubconf, led_pin=config["led_pin"])
    await hub.connect()

    def newrow(row, pin):
        print(f"now on row {row}")
        # Socket IO send event "rowstart" with data=row to every client in array sids
        hub.rowstart(sids, row)

    def rowcomplete(row, pin):
        print(f"row {row} completed!")
        # Socket IO send event "rowfinish" with data=row to every client in array sids
        hub.rowfinish(sids, row)

    s = Silversend(-20, 20, newrow=newrow, rowcomplete=rowcomplete)

    pattern = [False, True, False, False] * 10
    s.load(pattern)

    print("we can do things and we're starting")

    # Socket IO on event... this is also how you make more events
    @hub.on("row")
    async def row(data, sid):
        s.load(data)
        print(f"we got a row, which is {data}. Dope!")

    # Socket IO on event... this is also how you make more events
    @hub.on("subscribe")
    async def subscribe(data, sid):
        sids.append(sid)
        print(f"we appended the sid, they are now all {sids}!")

    while True:
        try:
            s.update()
            await a.sleep(0)
        except KeyboardInterrupt:
            print("Received exit, exiting")
            hub.close()
            break

a.run(main())
