import sys
import paho.mqtt.client as mqtt

class MqttClient(object):
  mqttc = None
  connected = False

  def on_connect(self, client, userdata, flags, rc):
      sys.stdout.write("MQTT:Connection returned result:" + mqtt.connack_string(rc) + "\n")

  def __init__(self, mqtt_host, mqtt_port, username, password, clientName):
    if mqtt_host.lower() != "none":
      sys.stdout.write("Initializing MQTT client...")
      sys.stdout.flush()

      self.mqttc = mqtt.Client( clientName )
      self.mqttc.username_pw_set(username, password)
      self.mqttc.on_connect=self.on_connect
      rc=self.mqttc.connect(mqtt_host, mqtt_port)
      if rc == 0:
        self.connected = True
        sys.stdout.write("connected!\n")
      else:
        self.connected = False
        sys.stdout.write("MQTT Connection failed with rc_code[" + rc + "].\n")

      self.mqttc.loop_start()

      sys.stdout.flush()
    else:
      print("Not initializing MQTT client. (mqtt_host is none).")

  def isConnected():
   return self.connected;

  def publish(self, mq_topic, line):
    if self.connected == False:
        print("Not publishing as we are not connected.")
        return

    # Publish to mqtt if client defined
    if self.mqttc is not None:
      info = self.mqttc.publish(mq_topic, line,1)
      info.wait_for_publish()
      if info.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Publish succeeded.")
      elif info.rc == mqtt.MQTT_ERR_NO_CONN:
        print("Publish failed(No Connection)")
      else:
        print("Publish failed with return_code["+info.rc+"]")
    else:
      print("Publish aborted:self.mqttc is null.")

