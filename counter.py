class Counter:
    def __init__(self, pin, init=0, rising=True, falling=False, d=1):
        self._pin = pin
        self._last = pin.value()
        self._init = init
        self._rising = rising
        self._falling = falling
        self._d = d

        self.reset()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def reset(self):
        self.value = self._init

    def update(self):
        val = self._pin.value()
        trig = (self._rising and not self._last and val) or (self._falling and self._last and not val)
        if trig:
            self.value += self._d
        self._last = val

