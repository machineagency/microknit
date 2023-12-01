from machine import Pin
import uasyncio as a


LED = 2

async def blink(on_ms=200, off_ms=800, pin=LED):
    led = Pin(pin, Pin.OUT)
    led.on()
    await a.sleep_ms(on_ms)
    led.off()
    await a.sleep_ms(off_ms)

async def blink_loop(on_ms=200, off_ms=800, pin=LED, debug=False):
    i = 0
    while True:
        i+= 1
        if debug:
            print(f"blink {i}")
        await blink(on_ms, off_ms, pin)

if __name__ == "__main__":
    a.run(blink_loop(100, 400))
