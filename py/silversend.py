from machine import Pin
from .counter import Counter


LED     = 2
CLOCK   = 13
CAMS    = 12
OUT     = 14
NEEDLE  = 27
DIRECTION = 26

RIGHT, LEFT = 0, 1

class Silversend:

    def __init__(self, lcam, rcam, newrow=None, rowcomplete=None, led=LED, clock=CLOCK, cams=CAMS, out=OUT, needle=NEEDLE, direction=DIRECTION):
        self.led = Pin(led, Pin.OUT)
        self.clock = Pin(clock, Pin.IN)          #DIN 1 ???
        self.cams = Pin(cams, Pin.IN)            #DIN 2 High inside point cams
        self.out = Pin(out, Pin.OUT)             #DIN 3 output high when slip
        self.needle = Pin(needle, Pin.IN)        #DIN 4 goes low whenever a needle is passed
        self.direction = Pin(direction, Pin.IN)  #DIN 5 direction, low = going right, high= left
                                                 #DIN 6 power +5V
                                                 #DIN 7 power +5V

        self.lcam = lcam
        self.rcam = rcam-1 # because 0 is not a numbered needle on the silver reed machine

        self.out.off()

        # Edge-triggered counters:

        # rising edge of needle pin -> triggers as soon as we finish moving over needle
        self.needle_counter = Counter(self.needle, init=lcam, d=1) #first needle will be needle 1
        # rising edge of cams pin -> triggers as soon as we start a row
        self.row_counter = Counter(self.cams, init=-1, d=1, callback=newrow) #first row will be row 0 because it increments once from init
        # falling edge of cams pin -> triggers as soon as we finish a row
        self.row_complete = Counter(self.cams, init=-1, d=1, rising=False, falling=True, callback=rowcomplete)

    def setcams(self, lcam, rcam):
        self.lcam = lcam
        self.rcam = rcam

    def setrowindex(self, row):
        self.row_counter.value = row
        self.row_complete.value = row

    def loadrow(self, line):
        self.line = line

    def update(self):
        self.row_counter.update()
        self.row_complete.update()
        #Are we in the cams? yes
        if self.cams.value() == 1:
            self.needle_counter.update()
            try:
                self.output()
            except IndexError:
                print(f"Index Error: {self.lcam}, {self.needle_counter.value}, {self.rcam}")

        #if we have left the cams:
        else:
            #print(self.row_counter.value)
            if self.direction.value() == RIGHT:
                self.needle_counter.reset(self.lcam, 1)
            else:
                self.needle_counter.reset(self.rcam, -1)

    def output(self):
        if (self.needle_counter.value < self.lcam) or (self.needle_counter.value > self.rcam):
            print(f"Needle index {self.needle_counter.value} is outside cam range ({self.lcam}..{self.rcam})")
            print("  -> defaulting to regular knit")
            self.led.off()
            self.out.off()
        elif self.line[self.needle_counter.value - self.lcam]:
            self.led.on()
            self.out.on()
        else:
            self.led.off()
            self.out.off()
