from machine import Pin


LED     = 2
CLOCK   = 13
CAMS    = 12
OUT     = 14
NEEDLE  = 27
DIRECTION = 26

DEBUG1   = 25
DEBUG2   = 33

RIGHT, LEFT = 0, 1

class Silversend:

    def __init__(self, lcam, rcam, rowstarting=None, rowcomplete=None, led=LED, clock=CLOCK, cams=CAMS, out=OUT, needle=NEEDLE, direction=DIRECTION):
        self.debug1 = Pin(DEBUG1, Pin.OUT)
        self.debug2 = Pin(DEBUG2, Pin.OUT)

        self.led = Pin(led, Pin.OUT)
        self.clock = Pin(clock, Pin.IN)          #DIN 1 ???
        self.cams = Pin(cams, Pin.IN)            #DIN 2 High inside point cams
        self.out = Pin(out, Pin.OUT)             #DIN 3 output high when slip
        self.needle = Pin(needle, Pin.IN)        #DIN 4 high when on a needle
        self.direction = Pin(direction, Pin.IN)  #DIN 5 direction, low = going right, high= left
                                                 #DIN 6 power +5V
                                                 #DIN 7 power +5V

        self.setcams(lcam, rcam)
        self.rowstarting = rowstarting
        self.rowcomplete = rowcomplete

        self.dostarting = False
        self.docomplete = False

        self.output = False
        self.led.off()
        self.out.off()

        self.row_index = -1
        self.needle_index = lcam
        self.needle_delta = 1 #when we go right, we add 1, when we go left, we subtract 1

        self.needle.irq(handler=self.needle_irq, trigger=Pin.IRQ_RISING) #Update needle index, set output pin in needle pin's ISR
        self.cams.irq(handler=self.cams_irq, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING) #Update row index, queue callbacks on cams pin's ISR

    def setcams(self, lcam, rcam):
        self.lcam = lcam
        self.rcam = rcam-1 # because 0 is not a numbered needle on the silver reed machine

    def setrowindex(self, row):
        self.row_index = row

    def loadrow(self, line):
        self.line = line

    def update(self):
        self.debug2.value(1)

        if self.dostarting:
            self.rowstarting(self.row_index)
            self.dostarting = False
        if self.docomplete:
            self.rowcomplete(self.row_index)
            self.docomplete = False

        self.debug1.value(self.needle_index & 0x1)
        self.debug2.value(0)

    def cams_irq(self, pin):
        if pin.value(): # rising edge
            self.row_index += 1
            self.dostarting = True
        else: # falling edge
            self.docomplete = True

    def needle_irq(self, pin):
        self.out.value(self.output)
        self.led.value(self.output)
        #Are we in the cams? yes
        self.needle_index += self.needle_delta
        if self.cams.value():
            idx = self.needle_index - self.lcam
            if idx < 0 or idx >= len(self.line):
                self.output = 0
            else:
                self.output = bool(self.line[idx])
        #if we have left the cams:
        else:
            self.output = 0
            #print(self.row_counter.value)
            if self.direction.value() == RIGHT:
                self.needle_index, self.needle_delta = self.lcam, 1
            else:
                self.needle_index, self.needle_delta = self.rcam, -1
