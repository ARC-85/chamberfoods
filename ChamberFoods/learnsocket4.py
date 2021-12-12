import time
import energenie

energenie.init()
s4 = energenie.Devices.OOKSwitch((0x12345, 4))

while True:
      s4.turn_on()
      time.sleep(3)
      s4.turn_off()
      time.sleep(3)