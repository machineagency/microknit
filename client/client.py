import time
from esphub import ESPHub

hub = ESPHub()
hub.filter('mpy')
hub.blink()
hub.loadrow([1,0]*10)
hub.subscribe()
hub.setcams([-10, 10])

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
