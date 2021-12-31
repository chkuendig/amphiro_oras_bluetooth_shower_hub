import abc
import mqtt
import random
import string

from AbstractWriter import AbstractWriter

from string import Template

class MQTTWriter(AbstractWriter):
    clientId = None
    mqtt_template = None
    mqttc = None

    def __init__(self, Config ):
      # Call abstract base class and pass the name of this sensor and name for the sensor
      AbstractWriter.__init__(self, Config )

      # Create random clientId for mqtt connection. (Must be unique inside Broker)
      self.clientId ="shower_mqtt_".join(random.choice(string.ascii_lowercase) for i in range(5))

      # Read MQTT messages structure from config file
      mqtt_message_format= Config.get("mqtt", "message_format")
      self.mqtt_template= Template(mqtt_message_format)

      # Read MQTT settings and init mqtt client with it.
      mqtt_host= Config.get("mqtt", "mqtt_host")
      mqtt_port= Config.getint("mqtt", "mqtt_port")
      mqtt_username= Config.get("mqtt", "mqtt_username")
      mqtt_password= Config.get("mqtt", "mqtt_password")

      print("MQTT-settings[" + mqtt_host + ":" + str(mqtt_port) + " " + mqtt_username+"]")

      # Initialize MQTT and Initialize connection
      self.mqttc = mqtt.MqttClient( mqtt_host, mqtt_port, mqtt_username, mqtt_password, self.clientId )



    # Write data to writers target (This is abstract method that is used to write data.)
    def write(self, dataDict, rawData1, rawData2 ):
           # Construct data and datavalue Dictionaries that will be sent to MQTT
           line = self.mqtt_template.substitute(mac=dataDict["mac"],sensor=dataDict["sensor"], utc=dataDict["utc"]  , second=dataDict["second"], session=dataDict["session"], temp=dataDict["temp"], kwatts=dataDict["kwatts"],pulses=dataDict["pulses"],liters=dataDict["liters"], liters_delta=dataDict["liters_delta"], flow=dataDict["flow"], f_c=dataDict["f_c"], a=dataDict["a"], b=dataDict["b"] )
           print("- publishing MQTT:"+line+" ", end="")
           self.mqttc.publish( "shower", line )
