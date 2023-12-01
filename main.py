import json
import uasyncio as a

from py.wifi import connect
from py.esphub import esphub
from py.silversend import Silversend

sids = []



with open("config.json") as f:
    config = json.load(f)
wificonf = config["wifi"]
esphubconf = config["esphub"]

async def main():
    wifi = await connect(**wificonf)
    hub = await esphub(**esphubconf, led_pin=config["led_pin"])
    
    def newrow(row, pin):
        print(f"now on row {row}")
        for sid in sids:
            data=dict(sid=sid, event='rowstart', data=row)
            a.create_task(hub.emit('command',data))
            print(f"data is {data}")
            
    def rowcomplete(row, pin):
        print(f"row {row} completed!")
        for sid in sids:
            data=dict(sid=sid, event='rowfinish', data=row)
            a.create_task(hub.emit('command',data))
            print(f"data is {data}")
    s = Silversend(-20, 20, newrow=newrow, rowcomplete=rowcomplete)

    pattern = [False, True, False, False] * 10
    s.load(pattern)

    print("we can do things and we're starting")

    @hub.on("row")
    async def row(data, sid):
        s.load(data)
        print(f"we got a row, which is {data}. Dope!")
        
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
