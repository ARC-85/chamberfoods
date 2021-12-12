import time
import energenie

energenie.init()
s3 = energenie.Devices.OOKSwitch((0x12345, 3))

while True:
      s3.turn_on()
      time.sleep(3)
      s3.turn_off()
      time.sleep(3)