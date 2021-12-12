from signal import pause
import BlynkLib
import logging
from dotenv import dotenv_values
import datetime
import time
from picamera import PiCamera
import storeFileFB
import time
import energenie
import RPi.GPIO as GPIO
import seeed_dht
import sys

energenie.init()
s1 = energenie.Devices.OOKSwitch((0x12345, 1))

  #load MQTT configuration values from .env file
config = dotenv_values(".env")
  # initialize Blynk
blynk = BlynkLib.Blynk(config['BLYNK_AUTH'])
  #configure Logging
logging.basicConfig(level=logging.INFO)

#exec(open("thingspeaktest.py").read())

setvalue=15
lastturnontime = time.time()
lastturnofftime = time.time()
turnedon = 0
turnedoff = 0
tempidletime = 10
#@blynk.on("V1")
#def v1_write_handler(value):
#      global setvalue
#      setvalue=int(value[0])
#      print(f'Current setpoint value: {setvalue}')

buttonvalue=0
@blynk.on("V0")
def v0_write_handler(value):
      global buttonvalue
      buttonvalue=value[0]
      print(f'Current button value: {buttonvalue}')
      if buttonvalue=="1":
        exec(open("takepicture.py").read())
            
            
            

while True:
    try:
      sensor = seeed_dht.DHT("22", 4)
      humi, temp = sensor.read()

      @blynk.on("V1")
      def v1_write_handler(value):
       global setvalue
       setvalue=int(value[0])
       print(f'Current setpoint value: {setvalue}')
      
      blynk.run()
      blynk.virtual_write(2, round(temp,2))
      blynk.virtual_write(3, round(humi,2))
      blynk.virtual_write(4, round(setvalue,2))

      print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp))
     
      rightnow = time.time()
      #print(f'Current time: {rightnow}')
      #print(f'Last turn on: {lastturnontime}')
      #print(f'Last turn off: {lastturnofftime}')
      print(f'Last turn on difference: {rightnow - lastturnontime}')
      print(f'Last turn off difference: {rightnow - lastturnofftime}')
      if setvalue < temp:
          if (rightnow - lastturnofftime) > tempidletime and turnedon==0:
              s1.turn_on()
              lastturnontime = time.time()
              turnedon=1
              turnedoff=0
      else: 
          if (rightnow - lastturnontime) > tempidletime and turnedoff==0:
              s1.turn_off()
              lastturnofftime = time.time()
              turnedoff = 1
              turnedon = 0

      
      time.sleep(3)
    
    except:
      logging.info('Interrupted')
