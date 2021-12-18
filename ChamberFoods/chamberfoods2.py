#import necessary libraries
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
#Define the controlable sockets for the ENER010 power adapter (S1-3) for each of the ENER314-RT channels (1-3). An arbitrary house code (12345) has been assigned
s1 = energenie.Devices.OOKSwitch((0x12345, 1))
s2 = energenie.Devices.OOKSwitch((0x12345, 2))
s3 = energenie.Devices.OOKSwitch((0x12345, 3))

#initialise DHT22 temperature/humidity sensor device, 22 refers to sensor type and 4 refers to GPIO pin for data connection
sensor = seeed_dht.DHT("22", 4) 

#load MQTT configuration values from .env file
config = dotenv_values(".env")
# initialize Blynk
blynk = BlynkLib.Blynk(config['BLYNK_AUTH'])
#configure Logging
logging.basicConfig(level=logging.INFO)

#define variables 
setvalue=15 #initial setpoint temperature. Will be changed by Blynk app slider widget (V1)
lastcoolingturnontime = time.time() #counter for the last time the fridge/cooler device was turned on relative to the current time
lastcoolingturnofftime = time.time() #counter for the last time the fridge/cooler device was turned off relative to the current time
lastheatingturnontime = time.time() #counter for the last time the heater device was turned on relative to the current time
lastheatingturnofftime = time.time() #counter for the last time the heater device was turned off relative to the current time
coolingturnedon = 0 #signal for fridge/cooler device turned on (value 1 or 0)
coolingturnedoff = 0 #signal for fridge/cooler device turned off (value 1 or 0)
heatingturnedon = 0 #signal for heater device turned on (value 1 or 0)
heatingturnedoff = 0 #signal for heater device turned off (value 1 or 0)
coolingtempidletime = 10 #idle time for defining amount of time between turning fridge/cooler device on/off. Recommended as 900 (i.e. 15 min) but set as 10 for demonstration purposes
heatingtempidletime = 10 #idle time for defining amount of time between turning heater device on/off. 
activatecoolingtempdiff = 4 #threshold above setpoint temperature before cooling device (fridge) will be activated
deactivatecoolingtempdiff = 2 #threshold above setpoint temperature before cooling device (fridge) will be deactivated from a previously activated state to avoid overshoot
activateheatingtempdiff = 4 #threshold below setpoint temperature before heating device will be activated 
deactivateheatingtempdiff = 2 #threshold below setpoint temperature before heating device will be deactivated from a previously activated state to avoid overshoot

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
      print(f'Last turn on difference: {rightnow - lastcoolingturnontime}') #in the console print the difference (seconds) between the current time and the last time the fridge was turned on
      print(f'Last turn off difference: {rightnow - lastcoolingturnofftime}') #in the console print the difference (seconds) between the current time and the last time the fridge was turned off
      print(f'Last heating turn on difference: {rightnow - lastheatingturnontime}') #in the console print the difference (seconds) between the current time and the last time the heater was turned on
      print(f'Last heating turn off difference: {rightnow - lastheatingturnofftime}') #in the console print the difference (seconds) between the current time and the last time the heater was turned off
      if setvalue <= temp: #check if setpoint is lower than current temperature (i.e cooling required)
          if (temp - setvalue) >= activatecoolingtempdiff and (rightnow - lastcoolingturnofftime) > coolingtempidletime and coolingturnedon==0: #to avoid overheating check if temperature above setpoint exceeds activation threshold and the time since last turning fridge off exceeds specified idle time and the fridge is not currently turned on
              s1.turn_on() #turn on socket 1 (i.e. fridge)
              lastcoolingturnontime = time.time() #update the last time fridge was turned on
              coolingturnedon=1 #update to signal fridge turned on
              coolingturnedoff=0 #update to signal fridge not turned off
          if (temp - setvalue) >= deactivatecoolingtempdiff and (rightnow - lastcoolingturnontime) > coolingtempidletime and coolingturnedon==1: #to avoid overshoot check if temperature above setpoint exceeds deactivation threshold and the time since last turning fridge on exceeds specified idle time and the fridge is currently turned on
              s1.turn_off() #turn off socket 1 (i.e. fridge)
              lastcoolingturnofftime = time.time() #update the last time fridge was turned off
              coolingturnedon=0 #update to signal fridge not turned on
              coolingturnedoff=1 #update to signal fridge turned off
          if (rightnow - lastheatingturnontime) > heatingtempidletime and heatingturnedoff==0: #in case heating overshoot check was missed, check if the time since last turning heating on exceeds specified idle time and the heating is not currently turned off
              s3.turn_off() #turn off socket 3 (i.e. heater)
              lastheatingturnofftime = time.time() #update the last time heater was turned off
              heatingturnedoff = 1 #update to signal heater is turned off
              heatingturnedon = 0 #update to signal heater is not turned on
      else: #otherwise if setpoint is higher than current temperature (i.e heating required)
          if (rightnow - lastcoolingturnontime) > coolingtempidletime and coolingturnedoff==0: #in case cooling overshoot check was missed, check if the time since last turning fridge on exceeds specified idle time and the fridge is not currently turned off
              s1.turn_off() #turn off socket 1 (i.e. fridge)
              lastcoolingturnofftime = time.time() #update the last time fridge was turned off
              coolingturnedoff = 1 #update to signal fridge is turned off
              coolingturnedon = 0 #update to signal fridge is not turned on
          if (setvalue - temp) >= activateheatingtempdiff and (rightnow - lastheatingturnofftime) > heatingtempidletime and heatingturnedon==0: #to avoid overcooling check if temperature below setpoint exceeds activation threshold and the time since last turning heater off exceeds specified idle time and the heater is not currently turned on
              s3.turn_on() #turn on socket 3 (i.e. heater)
              lastheatingturnontime = time.time() #update the last time heater was turned on
              heatingturnedon=1 #update to signal heater is turned on
              heatingturnedoff=0 #update to signal heater is not turned off
          if (setvalue - temp) >= deactivateheatingtempdiff and (rightnow - lastheatingturnontime) > heatingtempidletime and heatingturnedon==1: #to avoid overshoot check if temperature below setpoint exceeds deactivation threshold and the time since last turning heater on exceeds specified idle time and the heater is currently turned on
              s3.turn_off() #turn off socket 3 (i.e. heater)
              lastheatingturnofftime = time.time() #update the last time heater was turned off
              heatingturnedon=0 #update to signal heater is not turned on
              heatingturnedoff=1 #update to signal heater is turned off

      time.sleep(3) #wait 3 seconds before repeating loop
    
    except: #exception for not repeating loop
        logging.info('Interrupted') #log an interuption to the loop

