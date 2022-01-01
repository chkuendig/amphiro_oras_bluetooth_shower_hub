#!/usr/bin/python3
from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import BTLEDisconnectError

import time
import struct
import sys
import os
from os.path import exists

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

def initConfigFile(macAddress, enableHA ):
  print("Creating config.ini file for you, with your mac["+str(macAddress)+"]")

  f = open("config.ini.default", "r")
  configData = f.read()
  newConfigData = configData.replace("00:11:22:33:44:55", str(macAddress) )

  # If HA enabled, then change topic to something more convenient for HA
  if ( enableHA ):
     configData = newConfigData
     newConfigData = configData.replace("mqtt_topic=shower", "mqtt_topic=homeassistant/sensor/shower" )

  f2 = open("config.ini", "w")
  f2.write( newConfigData )
  f2.close()

# Check if this setup has already been executed. (We'll try to protect the config.ini with this checking.)
if (exists("config.ini") ):
  print("config.ini file already created!")
  print("Please delete it if you want to rerun setup again.")
  sys.exit(0)

# Ask if HA settings should be enabled.
ha_enabled = False
ha_reply = input("Are you going to send showers data to HomeAssistant [y/n]: ")
if ( ha_reply.lower() in ['true', '1', 't', 'y', 'yes']):
  print("Using HA favorable settings for you.")
  ha_enabled = True

print("\nRemember to turn on the water. Running water will turn on your shower head.")
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
                    print("Bluetooth shower head found at["+dev.addr+"].\n")
                    initConfigFile( dev.addr, ha_enabled )
                    print("Remember to change MQTT credentials from config.ini to match your settings.")
                    sys.exit(0)
                else:
                    # print( "Other device[" + str(ManuDataHex[0]) + ":" + str(ManuDataHex[1]) + "] ",dev.addr," RSSI=",dev.rssi," dB")
                    print(".", end="", flush=True)
                    continue

except (BTLEDisconnectError,IOError) as err:
  errorCounter +=1
  pass

except DecodeErrorException:
  pass

except KeyboardInterrupt:
  print('User exited.')
  sys.exit(0)

