#import necessary libraries
import BlynkLib
import logging
from dotenv import dotenv_values
import datetime
from picamera import PiCamera
import storeFileFB
import time


  #load MQTT configuration values from .env file
config = dotenv_values(".env")
  # initialize Blynk
blynk = BlynkLib.Blynk(config['BLYNK_AUTH'])
  #configure Logging
logging.basicConfig(level=logging.INFO)


camera = PiCamera() #activate RPi camera

frame = 1 #set variale for naming captured images
buttonvalue=0 #signal for button widget on Blynk app (V0) for controlling camera and lamp to take pictures (value 1 or 0)
#function using button widget on Blynk app for activating lamp and taking picture
@blynk.on("V0") #button is associated with virtual pin 0 (V0)
def v0_write_handler(value): #button sets value (1 or 0)
      global buttonvalue #declare global variable
      global frame #declare global variable
      buttonvalue=value[0] #variable set by value of button
      print(f'Current button value: {buttonvalue}')
      if buttonvalue=="1": #when button is pressed (i.e. value = 1)
            frame = 1 #set variale for naming captured images
            fileLoc = f'/home/pi/ChamberFoods/img/frame{frame}.jpg' # set variable for location of image file 
            currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") #set variable for current time
            camera.capture(fileLoc) # capture image and store in file location
            print(f'frame {frame} taken at {currentTime}') # print frame number to console
            storeFileFB.store_file(fileLoc) #use storeFileFB.py script for storing image in Firebase
            storeFileFB.push_db(fileLoc, currentTime) #use storeFileFB.py script for pushing image and time take to Firebase
            frame += 1 #update image number if multiple pictures taken

#indefinite loop
while True:
      blynk.run() #run Blynk
      time.sleep(3) #wait 3 seconds before repeating loop
         