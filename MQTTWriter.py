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
    mqtt_topic = None

    send_last_message = False
    mqtt_template_last = None
    mqtt_topic_last = None

    def __init__(self, Config ):
      # Call abstract base class and pass the name of this sensor and name for the sensor
      AbstractWriter.__init__(self, Config )

      # Create random clientId for mqtt connection. (Must be unique inside Broker)
      self.clientId ="shower_mqtt_".join(random.choice(string.ascii_lowercase) for i in range(5))

      # Read MQTT messages structure from config file
      self.mqtt_template= Template( Config.get("mqtt", "message_format") )
      self.mqtt_template_last= Template( Config.get("mqtt", "last_message_format") )

      # Read MQTT settings and init mqtt client with it.
      mqtt_host= Config.get("mqtt", "mqtt_host")
      mqtt_port= Config.getint("mqtt", "mqtt_port")
      mqtt_username= Config.get("mqtt", "mqtt_username")
      mqtt_password= Config.get("mqtt", "mqtt_password")

      self.mqtt_topic=Config.get("mqtt", "mqtt_topic")
      self.mqtt_topic_last=Config.get("mqtt", "mqtt_topic_last")

      # should we also send last message, when shower session ends?
      if ( Config.get("mqtt", "send_last_message").lower() in ['true', '1', 't', 'y', 'yes']):
          self.send_last_message = True

      print("MQTT-settings[" + mqtt_host + ":" + str(mqtt_port) + "] topic["+self.mqtt_topic+"] lastTopic["+self.mqtt_topic_last+"]"  + " username[" + mqtt_username+"]")

      # Initialize MQTT and Initialize connection
      self.mqttc = mqtt.MqttClient( mqtt_host, mqtt_port, mqtt_username, mqtt_password, self.clientId )


    def writeLastMessage(self, dataDict, rawData1, rawData2 ):
         if ( self.send_last_message == True ):
             # Construct data and datavalue Dictionaries that will be sent to MQTT
             line = self.mqtt_template_last.substitute(mac=dataDict["mac"],sensor=dataDict["sensor"], utc=dataDict["utc"]  , second=dataDict["second"], session=dataDict["session"], temp=dataDict["temp"], kwatts=dataDict["kwatts"],pulses=dataDict["pulses"],liters_rounded=dataDict["liters_rounded"],liters=dataDict["liters"], liters_delta=dataDict["liters_delta"], flow=dataDict["flow"], flow_pulses=dataDict["flow_pulses"], a=dataDict["a"], temperature_pulses=dataDict["temperature_pulses"] )
             print("- publishing Last MQTT message:"+line+" ", end="")
             self.mqttc.publish( self.mqtt_topic_last, line )

    # Write data to writers target (This is abstract method that is used to write data.)
    def write(self, dataDict, rawData1, rawData2 ):
           # Construct data and datavalue Dictionaries that will be sent to MQTT
           line = self.mqtt_template.substitute(mac=dataDict["mac"],sensor=dataDict["sensor"], utc=dataDict["utc"]  , second=dataDict["second"], session=dataDict["session"], temp=dataDict["temp"], kwatts=dataDict["kwatts"],pulses=dataDict["pulses"],liters_rounded=dataDict["liters_rounded"],liters=dataDict["liters"], liters_delta=dataDict["liters_delta"], flow=dataDict["flow"], flow_pulses=dataDict["flow_pulses"], a=dataDict["a"], temperature_pulses=dataDict["temperature_pulses"] )
           print("- publishing MQTT:"+line+" ", end="")
           self.mqttc.publish( self.mqtt_topic, line )
