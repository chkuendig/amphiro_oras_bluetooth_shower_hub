# Hub application for Amphiro/Oras Digital shower head

This application is reading your Amphiro/Oras Digital Shower head for **water consumption**, **water flow(l/min)** , **water temperature** and **shower length**. That data can be sent forward as MQTT or written into a file.

You can point MQTT messages to your favorite datalogging service for storage and visualization.

I'm running this in small Raspberry PI Zero, but any Bluetooth enabled Linux should work.

![title.png](images/title_small.png)

# Quick setup
- run `./check_and_install_prerequisites.sh` to install all needed libraries
- run `sudo python3 setup.py` to find out your showers mac address and create default **config.ini** for you.
- run `./read_Ampiro_shower.sh` to start collecting data from your shower

# HomeAssistant integration
- Change the "mqtt_topic" in config.ini to provided HA value. This way provided configuration.yaml can be used as-is.
- Enable MQTT Broker in your HomeAssistant installation.
- Change MQTT-settings in config.ini to point into your HomeAssistant MQTT broker.
- Use provided "home_assistant_example_configuration.yaml" in HomeAssistant.

# Longer setup with explanations :) 

## Installation and configuration

- Clone this GIT repository
- Find your showers mac address by running `sudo python3 setup.py`
   - **setup.py** will automatically create default **config.ini** for you. (from config.ini.default)
   -  You can also manually create **config.ini** and add your mac address into it.
- Edit your MQTT credentials into **config.ini** file.
- Enable/disable file logging and MQTT from **config.ini** file.

## Prerequisites and libraries needed

You can just run helper script that will check and install all the required libraries.
`./check_and_install_prerequisites.sh`

Or do the same thing manually:

- You need to have **Python3** installed
  - Install with `sudo apt-get install python3` in rasbian.
- make sure following python libraries are installed:
  - **paho-mqtt**  (Install with: `pip3 install paho-mqtt`)
  - **bluepy** (Install with: `pip3 install bluepy`)


## Running this application

Run the following command:
_(Script assumes this GIT is cloned to /home/pi/ )_
```
./read_Ampiro_shower.sh
```
- Application will start searching for the shower head.
- When water is turned on this application will connect into the shower head and start streaming data from it.
- When  water is turned off, shower  turns off the bluetooth and application disconnects. Application switches back to searching for the shower head to turn on again.

## Running this application automatically
You should make sure this application is always running by placing it into cron.

In Ubuntu/rasbian it's easily done by adding the following line into your crontab.
```
@reboot sleep 20 && /home/pi/amphiro_oras_bluetooth_shower_hub/read_Ampiro_shower.sh
```
This will make sure that application is executed 20 seconds after reboot. (20 sec delay to make sure all the services are up and running.)

# Roadmap

Ideas to be implemented in the future:
- Calculate your cumulated daily water consumption and add it into outgoing MQTT-messages

# License
This application is licensed under **[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)**
