#!/usr/bin/python3
import json
import mqtt

import sys
import binascii
import struct
from time import sleep
import time
from datetime import datetime

import string
import random

import configparser
config="config.ini"

from bluepy.btle import UUID, Peripheral
from bluepy.btle import BTLEDisconnectError

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

print("Using config file ["+config+"] ", end="")

def log( line ):
  if ( data_object != None):
    data_object.write(line+"\n")
  print( line )


# Settings. Read configuration file
Config = configparser.ConfigParser()
Config.read(config)

# Read MQTT settings and init mqtt client with it.
mqtt_host= Config.get("mqtt", "mqtt_host")
mqtt_port= Config.getint("mqtt", "mqtt_port")
mqtt_username= Config.get("mqtt", "mqtt_username")
mqtt_password= Config.get("mqtt", "mqtt_password")
mqtt_enabled = False;

# Check if mqtt logging is enabled in config file
if ( Config.get("mqtt", "mqtt_enabled").lower() in ['true', '1', 't', 'y', 'yes']):
  mqtt_enabled = True;

# Get MAC address from config file.
MAC_ADDRESS= Config.get("general", "shower_mac_address")

# Get backup file name from config and  intialize it.
dumpfile=""
data_object=None
if ( Config.has_option("general", "datafile") ):
  dumpfile=Config.get("general", "datafile")
  data_object = open( dumpfile, 'a')

print("General settings[mac:" + MAC_ADDRESS + " file:" + dumpfile  + "] ", end="");
print("MQTT-settings[" + mqtt_host + ":" + str(mqtt_port) + " " + mqtt_username+"]")
print()

# Create random clientId for mqtt connection. (Must be unique inside Broker)
mqttClientId ="shower_mqtt_".join(random.choice(string.ascii_lowercase) for i in range(5))

# Initialize MQTT and Initialize connection
if (mqtt_enabled): mqttc = mqtt.MqttClient( mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqttClientId )

############ MAIN LOOP HERE ####################

try:

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
       data = {}

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

                # print( "  size=("+str(len(binvalStatus))+") ", end="")
                # print ("  0x"+ format(ch.getHandle(),'02X')  +"   "+str(ch.uuid) +" " + ch.propertiesToString() )

		# Construct data and datavalue Dictionaries that will be sent to MQTT
                datavalue={}
                datavalue["second"]=secs
                datavalue["count"]=startCounter
                datavalue["temp"]=temp
                datavalue["kwatts"]=kwatts
                datavalue["pulses"]=pulses
                datavalue["liters"]=pulses/2560
                datavalue["liters_delta"]= round( (pulses/2560) - previousLiters, 2)
                datavalue["flow"]=round( flow/1220, 2 )
                datavalue["f_c"]=flow
                datavalue["a"]=a
                datavalue["b"]=b

                data = {}
                data["utc"] = int(time.time()) # Absolute UTC EPOCH TIME for MQTT
                data["sensor"] = "shower"
                data['value'] = datavalue

		# Save current listers to "previous liters" so we can calculate delta liters on next round
                previousLiters = pulses/2560

                # print(data)

                line = json.dumps(data)
                print("- publishing MQTT:"+line+" ", end="")
                log( "--" + str(datetime.now()) + "--" )
                log( "1# " + v1 )
                log( "2# " + v2 )
                log( "3# " + line )
                log( "" );


                if (mqtt_enabled): mqttc.publish( "shower", line )

                #print ( "-count:" + str(val)[0:8] + " [" + str(startCounter) +"]" )
                #print ( "-temp:" + str(val)[30:32] + " [" + str(temp) + "]°C" )
                #print ( "-Watts:" + str(val)[26:30] + " [" + str(kwatts) + "]kWh" )
                #print ( "-Pulses:" + str(val)[26:30] + " [" + str(pulses) + "] -> [" + str(pulses/2560) + "]liters" )
                # print ( "-a:" + str(val)[14:18] + " [" + str(a) + "]")

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
