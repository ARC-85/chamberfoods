#importing required libraries
from dotenv import dotenv_values
import datetime
from picamera import PiCamera
import storeFileFB
import time

#activate RPi camera
camera = PiCamera()

frame = 1 #set variale for naming captured images
fileLoc = f'/home/pi/ChamberFoods/img/frame{frame}.jpg' # set variable for location of image file 
currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") #set variable for current time
camera.capture(fileLoc) # capture image and store in file location
print(f'frame {frame} taken at {currentTime}') # print frame number to console
storeFileFB.store_file(fileLoc) #use storeFileFB.py script for storing image in Firebase
storeFileFB.push_db(fileLoc, currentTime) #use storeFileFB.py script for pushing image and time take to Firebase
frame += 1 #update image number if multiple pictures taken
camera.close() #close the camera to avoid resource errors

         