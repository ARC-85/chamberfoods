#importing required libraries
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

#initialise the Energenie devices (ENER314-RT and ENER010)
energenie.init()
#Define the controlable sockets for the ENER010 power adapter (S1-2) for each of the ENER314-RT channels (1-2). An arbitrary house code (12345) has been assigned
s1 = energenie.Devices.OOKSwitch((0x12345, 1))
s2 = energenie.Devices.OOKSwitch((0x12345, 2))

#initialise DHT22 temperature/humidity sensor device, 22 refers to sensor type and 4 refers to GPIO pin for data connection
sensor = seeed_dht.DHT("22", 4)

#load MQTT configuration values and Blynk authorisation code from .env file
config = dotenv_values(".env")
# initialize Blynk with authorisation code
blynk = BlynkLib.Blynk(config['BLYNK_AUTH'])
#configure Logging
logging.basicConfig(level=logging.INFO)

#define variables
setvalue=25 #initial setpoint temperature. Will be changed by Blynk app slider widget (V1)
lastturnontime = time.time() #counter for the last time the fridge/cooler device was turned on relative to the current time
lastturnofftime = time.time() #counter for the last time the fridge/cooler device was turned off relative to the current time
turnedon = 0 #signal for fridge/cooler device turned on (value 1 or 0)
turnedoff = 0 #signal for fridge/cooler device turned off (value 1 or 0)
tempidletime = 10 #idle time for defining amount of time between turning fridge/cooler device on/off. Recommended as 900 (i.e. 15 min) but set as 10 for demonstration purposes
buttonvalue=0 #signal for button widget on Blynk app (V0) for controlling camera and lamp to take pictures (value 1 or 0)

#function using button widget on Blynk app for activating lamp and taking picture
@blynk.on("V0") #button is associated with virtual pin 0 (V0)
def v0_write_handler(value): #button sets value (1 or 0)
      global buttonvalue #declare global variable
      buttonvalue=value[0] #variable set by value of button 
      print(f'Current button value: {buttonvalue}') #track change in value through console
      if buttonvalue=="1": #when button is pressed (i.e. value = 1)
        s2.turn_on() #socket 2 turns on (lamp)
        time.sleep(2) #duration of 2 seconds
        exec(open("takepicture.py").read()) #takepicture.py script is called and run
        time.sleep(2) #lamp waits a further 2 seconds
        s2.turn_off() #lamp is turned off

#function for using the slider function on Blynk app to set temperature setpoint value         
@blynk.on("V1") #slider is associated with virtual pin 1 (V1)
def v1_write_handler(value): #slider sets value (5 to 50)
      global setvalue #declare global variable
      setvalue=int(value[0]) #variable set by value of slider
      print(f'Current setpoint value: {setvalue}') #track change in value through console

#indefinite loop
while True:
    try:
      
      #defining humidity and temperature variables for reading from sensor
      humi, temp = sensor.read()

      blynk.run() #run Blynk
      blynk.virtual_write(2, round(temp,2)) #write values to virtual pin 2 (value display) from rounded temperature readings
      blynk.virtual_write(3, round(humi,2)) #write values to virtual pin 3 (value display) from rounded humidity readings
      blynk.virtual_write(4, round(setvalue,2)) #write values to virtual pin 4 (value display) from setvalue variable - used as a check that slider is being read

      print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp)) #print the sensor type, temperature, and humidity values in the console
     
      rightnow = time.time() #set variable for current time
      print(f'Last turn on difference: {rightnow - lastturnontime}') #in the console print the difference (seconds) between the current time and the last time the fridge was turned on
      print(f'Last turn off difference: {rightnow - lastturnofftime}') #in the console print the difference (seconds) between the current time and the last time the fridge was turned off
      if setvalue <= temp: #check if setpoint is lower than current temperature (i.e cooling required)
          if (rightnow - lastturnofftime) > tempidletime and turnedon==0: #check if the time since last turning fridge off exceeds specified idle time and the fridge is not currently turned on
              s1.turn_on() #turn on socket 1 (i.e. fridge)
              lastturnontime = time.time() #update the last time fridge was turned on
              turnedon=1 #update to signal fridge turned on
              turnedoff=0 #update to signal fridge not turned off
      else: #otherwise if setpoint is higher than current temperature (i.e no cooling required)
          if (rightnow - lastturnontime) > tempidletime and turnedoff==0: #check if the time since last turning fridge on exceeds specified idle time and the fridge is not currently turned off
              s1.turn_off() #turn off socket 1 (i.e. fridge)
              lastturnofftime = time.time() #update the last time fridge was turned off
              turnedoff = 1 #update to signal fridge turned off
              turnedon = 0 #update to signal fridge not turned om

      time.sleep(3) #wait 3 seconds before repeating loop
    
    except: #exception for not repeating loop
      logging.info('Interrupted') #log an interuption to the loop
