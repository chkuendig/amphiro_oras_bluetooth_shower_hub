#!/usr/bin/python3
import sys
import binascii
import struct
from time import sleep
import time
from datetime import datetime

import FileWriter
import MQTTWriter

import configparser

from bluepy.btle import UUID, Peripheral
from bluepy.btle import BTLEDisconnectError

configFile="config.ini"

# All data writer objects will be initialized in here
writers = []

# Error counter is used to track how many disconnections in a row we are getting.
errorCounter = 0

MAC_ADDRESS=""
uuids={
	"name" :"00002a29-0000-1000-8000-00805f9b34fb",
	"version":"00002a26-0000-1000-8000-00805f9b34fb",
	"status":"7f402203-504f-4c41-5261-6d706869726f",
        "flow":"7f40c00f-504f-4c41-5261-6d706869726f",
        }


print( datetime.now() )

print("Using config file ["+configFile+"] ", end="")

# Settings. Read configuration file
Config = configparser.ConfigParser()
Config.read(configFile)

# Get MAC address from config file.
MAC_ADDRESS= Config.get("general", "shower_mac_address")
SHOWER_ID = Config.get("general", "shower_name")

print("General settings[mac:" + MAC_ADDRESS + " id:"+SHOWER_ID+"] ", end="");


try:
 # Initialize file writer
 if ( Config.get("general", "write_to_file").lower() in ['true', '1', 't', 'y', 'yes']):
    writers.append( FileWriter.FileWriter(Config) )

 # Check if mqtt logging is enabled in config file
 if ( Config.get("general", "mqtt_enabled").lower() in ['true', '1', 't', 'y', 'yes']):
    writers.append( MQTTWriter.MQTTWriter(Config) )

 ############ MAIN LOOP HERE ####################


 while(True):

  try:
   print("Connecting: ", flush=True,end="")
   p = Peripheral( MAC_ADDRESS,"public")
   chStatus = p.getCharacteristics( uuid= uuids["status"] )[0]
   chFlow   = p.getCharacteristics( uuid= uuids["flow"]   )[0]
   print("")

   # Connection established if we got here. Reset error counter.
   errorCounter = 0

   # Just doing some double checking to make sure we got correct UUID's
   if ( chStatus.supportsRead() and chFlow.supportsRead() ):

       previousLiters = 0

       # Infinite loop for reading value as long as they are available.
       # (Exception will break this loop when shower turns off and disconnects.)
       while(True):
                binvalStatus = chStatus.read()

                val = binascii.b2a_hex(binvalStatus)

		# Construct v1 containing spaced out representation of the raw data
                v1 = ""
                startCounter = int( val[2:6],16 )
                v1 += str(val)[0:8] + " "

                secs = int( val[6:10],16 )
                v1 +=str(val)[8:12] + " "

                v1 +=str(val)[12:14] + " "

                a = int( val[12:16],16 )
                v1 +=str(val)[14:18] + " "

                pulses = int( val[16:22],16 )
                v1 +=str(val)[18:24] + " "

                temp = int( val[22:24],16 )
                v1 +=str(val)[24:26] + " "

                kwatts = int( val[24:28],16 )/100
                v1 +=str(val)[26:30] + " "

		# Constant 19?
                v1 +=str(val)[30:32] + " "

                v1 +=str(val)[32:]

		# READ FLOW UUID
                binvalFlow = chFlow.read()
                valFlow = binascii.b2a_hex(binvalFlow)

		# Construct v2 containing spaced out representation of the raw data
                v2  = ""
                v2 += str(valFlow)[0:6] + " "
                v2 += str(valFlow)[6:10] + " "

                flow = int( valFlow[8:12],16 )
                v2 += str(valFlow)[10:14] + " "

                b = int( valFlow[12:16],16 )
                v2 += str(valFlow)[14:18] + " "
                v2 += str(valFlow)[18:]

		# Construct Data Dictionary object that will be passed to all available Writers
                data = {};
                data["utc"] = int(time.time())
                data["sensor"] = SHOWER_ID
                data["session"]=startCounter
                data["second"]=secs
                data["temp"]=temp
                data["kwatts"]=kwatts
                data["pulses"]=pulses
                data["liters"]=round( pulses/2560, 2)
                data["liters_delta"]= round( (pulses/2560) - previousLiters, 2)
                data["flow"]=round( flow/1220, 2 )
                data["f_c"]=flow
                data["a"]=a
                data["b"]=b

		# Save current listers to "previous liters" so we can calculate delta liters on next round
                previousLiters = pulses/2560

                for i in range(len(writers)):
                   writers[i].write(data, v1, v2)

                print("sleeping", end="")
                for x in range(5):
                  print(".", flush=True, end="")
                  sleep(1)
                print("")

  except (BTLEDisconnectError,IOError) as err:
    print("BLE Connection failed["+type(err).__name__+"]. ")
    errorCounter +=1

    if (errorCounter < 10 ):
      print("Reconnecting in 5 seconds", flush=True, end="")
      for x in range(5):
         print(".", flush=True, end="")
         sleep(1)
    else:
      print("[" + str(err) + "] ", end="")
      print("Shower seems to be offline. Sleeping for 60 seconds and trying to connect again.")
      sleep(60)

#  except BaseException as err:
#      print(err)
#      print("BaseException. Something is really broken. Sleeping for 5 minutes before retrying.")
#      sleep(300)


except KeyboardInterrupt:
  print('User exited.')
  sys.exit(0)
