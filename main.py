import machine
import json
import time

from py.silversend import Silversend

uart = machine.UART(0, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

led = machine.Pin(2, machine.Pin.OUT)
led.on()

def rx():
    if uart.any():
        data = uart.readline()
        return json.load(data)
    return None

def send(event, data):
    uart.write(json.dumps([event, data]))

def rowstarting(row):
    send('rowstart', row)

def rowcomplete(row):
    send('rowfinish', row)

'''
s = Silversend(-20, 20, rowstarting=rowstarting, rowcomplete=rowcomplete)
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

a.run(main())
'''

while True:
    try:
        send('got', [0, 1])
        time.sleep(1)
        led.value(1-led.value())
    except KeyboardInterrupt:
        break

