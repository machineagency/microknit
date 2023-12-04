import time
from esphub import ESPHub

hub = ESPHub()
hub.filter('mpy')
hub.blink()
hub.loadrow([1,0,1,1]*10)
hub.subscribe()
time.sleep(10)
hub.setrowindex(2)
