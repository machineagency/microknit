import network
import uasyncio as a


# ssid - network name
# password - password
# attempts - how many time will we try to connect to WiFi in one cycle
# delay_in_msec - delay duration between attempts
async def connect(ssid, password, attempts = 100, delay_in_msec = 200, stretch=1.2):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(1)

    for i in range(attempts):
        print(f"WiFi connecting to <{ssid}> with password <{password}> -- Attempt {i}.")
        if wifi.status() != network.STAT_CONNECTING:
            wifi.connect(ssid, password)
        await a.sleep_ms(int(delay_in_msec))
        if wifi.isconnected():
            print(f"ifconfig: {wifi.ifconfig()}")
            return wifi
        await a.sleep_ms(int(delay_in_msec))
        delay_in_msec *= stretch

    print("Wifi not connected.")
    return None

if __name__ == "__main__":
    import json
    with open("config.json") as f:
        config = json.load(f)
    wificonf = config["wifi"]

    async def main():
        while True:
            print("Connecting to wifi...")
            wifi = await connect(**wificonf)
            if wifi:
                print("Connected.")
                return

    a.run(main())
