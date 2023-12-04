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
        self.row_counter = Counter(self.cams, init=0, d=1, callback=newrow) #first row will be row 1
        # falling edge of cams pin -> triggers as soon as we finish a row
        self.row_complete = Counter(self.cams, init=0, d=1, rising=False, falling=True, callback=rowcomplete)        

    def load(self, line):
        self.line = line

    def update(self):
        self.row_counter.update()
        self.row_complete.update()
        #Are we in the cams? yes
        if self.cams.value() == 1:
            self.needle_counter.update()
            self.output()
        #if we have left the cams:
        else:
            #print(self.row_counter.value)
            if self.direction.value() == RIGHT:
                self.needle_counter.reset(self.lcam, 1)
            else:
                self.needle_counter.reset(self.rcam, -1)

    def output(self):
        if self.line[self.needle_counter.value]:
            self.led.on()
            self.out.on()
        else:
            self.led.off()
            self.out.off()
