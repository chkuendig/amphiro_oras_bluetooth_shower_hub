from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import BTLEDisconnectError

import time
import struct
import sys
import os

if os.geteuid() != 0:
    exit("You need to have root privileges to run Bluetooth scanner.\nPlease try again, this time using 'sudo'. Exiting.")

class DecodeErrorException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

scanner = Scanner().withDelegate(ScanDelegate())

print("Remember to turn on the water. Running water will turn on your shower head.")
print("Searching for Bluetooth shower head:", end="", flush=True)

try:
    while 1:
        print(".", end="",flush=True)
        devices = scanner.scan(2.0)

        for dev in devices:
            ManuData = ""
            ManuDataHex = []
            for (adtype, desc, value) in dev.getScanData():
                if (desc == "Manufacturer"):
                    ManuData = value

                if (ManuData == ""):
                    continue

                for i, j in zip (ManuData[::2], ManuData[1::2]):
                    ManuDataHex.append(int(i+j, 16))

                #Try to find by manufacturer data
                if ((ManuDataHex[0] == 0xee) and (ManuDataHex[1] == 0xfa)):
                    # print ("Amphiro:" ,dev.addr , ", RSSI=",dev.rssi," dB")
                    print("\nBluetooth shower head found at["+dev.addr+"]. Add this mac address to config.ini")
                    sys.exit(0)
                else:
                    # print( "Other device[" + str(ManuDataHex[0]) + ":" + str(ManuDataHex[1]) + "] ",dev.addr," RSSI=",dev.rssi," dB")
                    print(".", end="", flush=True);
                    continue

except (BTLEDisconnectError,IOError) as err:
  errorCounter +=1
  pass

except DecodeErrorException:
  pass

except KeyboardInterrupt:
  print('User exited.')
  sys.exit(0)

