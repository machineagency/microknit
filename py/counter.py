class Counter:
    def __init__(self, pin, init=0, rising=True, falling=False, d=1, callback=None):
        self._pin = pin
        self._last = pin.value()
        self._init = init
        self._rising = rising
        self._falling = falling
        self._d = d
        self._callback = callback

        self.reset()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def reset(self, init=None, d=None):
        if init is not None:
            self._init = init
        if d is not None:
            self._d = d
        self.value = self._init

    def update(self):
        val = self._pin.value()
        trig = (self._rising and not self._last and val) or (self._falling and self._last and not val)
        if trig:
            self.value += self._d
            if self._callback:
                self._callback(self.value, val)
        self._last = val

if __name__ == "__main__":
    from machine import Pin
    import time

    def callback(value, pin):
        print(f"Pin became {pin} to get {value}")

    boot = Pin(0, Pin.IN) # Boot button
    c = Counter(boot, callback=callback)

    while True:
        c.update()
        print(c.value)
        time.sleep(0.1)
