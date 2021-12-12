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


camera = PiCamera()

      

frame = 1
buttonvalue=0
@blynk.on("V0")
def v0_write_handler(value):
      global buttonvalue
      global frame
      buttonvalue=value[0]
      print(f'Current button value: {buttonvalue}')
      if buttonvalue=="1":
            fileLoc = f'/home/pi/ChamberFoods/img/frame{frame}.jpg' # set location of image file and current time
            currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            camera.capture(fileLoc) # capture image and store in fileLoc
            print(f'frame {frame} taken at {currentTime}') # print frame number to console
            storeFileFB.store_file(fileLoc)
            storeFileFB.push_db(fileLoc, currentTime)
            frame += 1

while True:
      blynk.run()
      time.sleep(3)
         