import time
import energenie

energenie.init()
s1 = energenie.Devices.OOKSwitch((0x12345, 1))

while True:
      s1.turn_on()
      time.sleep(3)
      s1.turn_off()
      time.sleep(3)
         