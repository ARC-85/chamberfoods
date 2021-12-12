import time
import energenie

energenie.init()
s2 = energenie.Devices.OOKSwitch((0x12345, 2))

while True:
      s2.turn_on()
      time.sleep(3)
      s2.turn_off()
      time.sleep(3)
         