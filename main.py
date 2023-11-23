from machine import Pin
import time
from counter import Counter


LED = Pin(2, Pin.OUT)

CLOCK = Pin(13, Pin.IN)		#DIN 1
CAMS = Pin(12, Pin.IN)		#DIN 2 High inside point cams 
OUT = Pin(14, Pin.OUT)		#DIN 3 "output"? 
NEEDLE_TICKER = Pin(27, Pin.IN)	#DIN 4 goes low whenever a needle is passed 
DIRECTION = Pin(26, Pin.IN)	#DIN 5 direction, low = going right, high= left 
#				#DIN 6 possibly power, don't connect this
#				#DIN 7 also possibly power

CURRENT_DIRECTION = 0 #0 is going right 1 is going left
INSIDE_CAMS = 0
CURRENT_NEEDLE = 0
needle_counter = Counter(NEEDLE_TICKER)
print("we can do things and we're starting")

while True:
#    print(f"Clock: {CLOCK.value()}")
#    print(f"Cams: {CAMS.value()}")
#    print(f"Out: {OUT.value()}")
#    print(f"Needle ticker: {NEEDLE_TICKER.value()}")
#    print(f"Clock: {DIRECTION.value()}")
#    time.sleep(0.05)

    
    OUT.off()
    CURRECT_DIRECTION = 0
    INSIDE_CAMS = 0
    
    #where are we going
    if DIRECTION.value() == 0:
        CURRENT_DIRECTION = 0
        #print("Going right!")
    elif DIRECTION.value() == 1:
        CURRENT_DIRECTION = 1
        #print("Going left!")
         
    #Are we in the cams? yes
    if CAMS.value() == 1:
        INSIDE_CAMS = 1
        needle_counter.update()
        print(needle_counter.value)
        if needle_counter.value%3 == 0:
            LED.on()
        else:
            LED.off()
    
    #if we have left the cams:
    elif CAMS.value() == 0:
        INSIDE_CAMS = 0
        needle_counter.reset()
        
    


    
    
        
