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
from bluepy.btle import BTLEInternalError

configFile="config.ini"

# All data writer objects will be initialized in here
writers = []

# Error counter is used to track how many disconnections in a row we are getting.
errorCounter = 0

# True/False Dictionary defining if last message of shower session was sent. (Indexed with mac address)
lastMessageSent = {}

MAC_ADDRESS=""
uuids={
	"name" :"00002a29-0000-1000-8000-00805f9b34fb",
	"version":"00002a26-0000-1000-8000-00805f9b34fb",
	"status":"7f402203-504f-4c41-5261-6d706869726f",
        "flow":"7f40c00f-504f-4c41-5261-6d706869726f",
        }


def pause_with_dots(secs):
  for x in range(5):
     print(".", flush=True, end="")
     sleep(1)
  print("")

print( datetime.now() )

print("Using config file ["+configFile+"] ", end="")

# Settings. Read configuration file
Config = configparser.ConfigParser()
Config.read(configFile)

# Get Showers ID from config file.
SHOWER_ID = Config.get("general", "shower_name")

lastData = {}

# Read shower MAC address and remove possible white space from config
MAC_ADDRESSES= Config.get("general", "shower_mac_addresses").split(",")
for i in range(len(MAC_ADDRESSES)):
  mac = MAC_ADDRESSES[i].strip()
  MAC_ADDRESSES[i] = mac
  lastMessageSent[mac] = False
  lastData[mac] = {}


print("General settings[mac:" +str(MAC_ADDRESSES) + " id:"+SHOWER_ID+"] ", end="");

try:
 # Initialize file writer
 if ( Config.get("general", "file_write_enabled").lower() in ['true', '1', 't', 'y', 'yes']):
    writers.append( FileWriter.FileWriter(Config) )

 # Check if mqtt logging is enabled in config file
 if ( Config.get("general", "mqtt_enabled").lower() in ['true', '1', 't', 'y', 'yes']):
    writers.append( MQTTWriter.MQTTWriter(Config) )

 ############ MAIN LOOP HERE ####################


 while(True):

 # Loop all shower heads
  for s in range(len(MAC_ADDRESSES)):
   MAC_ADDRESS = MAC_ADDRESSES[s]

   try:
    print("Connecting["+str(s)+"][" + MAC_ADDRESS + "]: ", flush=True,end="")
    p = Peripheral( MAC_ADDRESS,"public")
    chStatus = p.getCharacteristics( uuid= uuids["status"] )[0]
    chFlow   = p.getCharacteristics( uuid= uuids["flow"]   )[0]
    print("")

    # Connection established if we got here. Reset error counter.
    errorCounter = 0
    lastMessageSent[MAC_ADDRESS] = False

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
                data["mac"] = MAC_ADDRESS.replace(":","_")
                data["session"]=startCounter
                data["second"]=secs
                data["temp"]=temp
                data["kwatts"]=kwatts
                data["pulses"]=pulses
                data["liters"]=round( pulses/2560, 2)
                data["liters_rounded"]=round( pulses/2560 )
                data["liters_delta"]= round( (pulses/2560) - previousLiters, 2)
                data["flow"]=round( flow/1220, 2 )
                data["f_c"]=flow
                data["a"]=a
                data["b"]=b

		# Store last received data for later use.
                lastData[MAC_ADDRESS] = data

		# Save current listers to "previous liters" so we can calculate delta liters on next round
                previousLiters = pulses/2560

                for i in range(len(writers)):
                   writers[i].write(data, v1, v2)

                print("sleeping", end="", flush=True)
                pause_with_dots(5)

   except (BTLEDisconnectError,BTLEInternalError,IOError) as err:
     print("BLE Connection failed["+type(err).__name__+"]. ")
     errorCounter +=1

     if (errorCounter <= 5 ):
       print("Reconnecting in 5 seconds", flush=True, end="")
       pause_with_dots(5)

     else:
       print("[" + str(err) + "] ", end="")
       print("Shower seems to be offline. Sleeping for 60 seconds and trying to connect again.")

       if (lastMessageSent[MAC_ADDRESS] == False):
          print("Shower offline. Sending last event message.")
          for i in range(len(writers)):
             print(lastData[MAC_ADDRESS]);

             if (len(lastData[MAC_ADDRESS]) > 0 ):
               writers[i].writeLastMessage(data, v1, v2)
             else:
               print("Do data received yet. Not sending last message out.")
          lastMessageSent[MAC_ADDRESS] = True

       sleep(60)

#  except BaseException as err:
#      print(err)
#      print("BaseException. Something is really broken. Sleeping for 5 minutes before retrying.")
#      sleep(300)


except KeyboardInterrupt:
  print('User exited.')
  sys.exit(0)
