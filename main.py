import json
import uasyncio as a

from py.wifi import connect
from py.esphub import ESPHub
from py.silversend import Silversend

sids = set()



with open("config.json") as f:
    config = json.load(f)
wificonf = config["wifi"]
esphubconf = config["esphub"]

async def main():
    wifi = await connect(**wificonf)
    hub = ESPHub(**esphubconf, led_pin=config["led_pin"])
    await hub.connect()

    def newrow(row, pin):
        # print(f"now on row {row}")
        # Socket IO send event "rowstart" with data=row to every client in array sids
        hub.rowstart(sids, row)

    def rowcomplete(row, pin):
        print(f"row {row} completed!")
        # Socket IO send event "rowfinish" with data=row to every client in array sids
        hub.rowfinish(sids, row)

    s = Silversend(-20, 20, newrow=newrow, rowcomplete=rowcomplete)

    pattern = [0, 1] * 20
    s.loadrow(pattern)

    print("we can do things and we're starting")

    # Socket IO on event... this is also how you make more events
    @hub.on("setcams")
    async def row(data, sid):
        s.setcams(*data)
        print(f"we are resetting the cam positions to {data}. Dope!")

    # Socket IO on event... this is also how you make more events
    @hub.on("setrowindex")
    async def row(data, sid):
        s.setrowindex(data)
        print(f"we are resetting the row counter to {data}. Dope!")

    # Socket IO on event... this is also how you make more events
    @hub.on("loadrow")
    async def row(data, sid):
        s.loadrow(data)
        print(f"we got a row, which is {data}. Dope!")

    # Socket IO on event... this is also how you make more events
    @hub.on("subscribe")
    async def subscribe(data, sid):
        sids.add(sid)
        print(f"we added {sid}, they are now all {sids}!")

    # Socket IO on event... this is also how you make more events
    @hub.on("unsubscribe")
    async def subscribe(data, sid):
        sids.remove(sid)
        print(f"we removed {sid}, they are now all {sids}!")

    while True:
        try:
            s.update()
            await a.sleep(0)
        except KeyboardInterrupt:
            print("Received exit, exiting")
            hub.close()
            break

a.run(main())
