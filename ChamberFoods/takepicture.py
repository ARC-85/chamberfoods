
from dotenv import dotenv_values
import datetime
from picamera import PiCamera
import storeFileFB
import time




camera = PiCamera()
frame = 1
fileLoc = f'/home/pi/ChamberFoods/img/frame{frame}.jpg' # set location of image file and current time
currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
camera.capture(fileLoc) # capture image and store in fileLoc
print(f'frame {frame} taken at {currentTime}') # print frame number to console
storeFileFB.store_file(fileLoc)
storeFileFB.push_db(fileLoc, currentTime)
frame += 1
camera.close()

         