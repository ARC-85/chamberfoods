import RPi.GPIO as GPIO
import seeed_dht



import sys
typ = '22'
if len(sys.argv) >= 3:
    typ = sys.argv[2]

import time
sensor = seeed_dht.DHT("22", 4)

while True:
    humi, temp = sensor.read()
    if not humi is None:
        print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp))
    else:
        print('DHT{0}, humidity & temperature: {1}'.format(sensor.dht_type, temp))
    time.sleep(1)
