import serial
import time
import json


port = '/dev/ttyUSB0'
baud = 115200
ser = serial.Serial(port, baud)

def send(event, data):
    ser.write(json.dumps([event, data]).encode())

try:
    send('setcams', [-10, 10])
    send('loadrow', [0, 1] * 10)
    while True:
        rx = ser.readline()
        if rx:
            print(rx)
        else:
            print ('.')
        time.sleep(1)
except Exception as e:
    print(e)
    ser.close()


