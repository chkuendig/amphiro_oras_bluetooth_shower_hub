# Hub application for Amphiro/Oras Digital shower head

This application is reading your Amphiro/Oras Digital Shower head for **water consumption**, **water temperature** and **shower length** and passes that data forward as MQTT.
You can point those MQTT messages to your favorite datalogging service for storage and visualization.

## Installation and configuration

- Clone this GIT repository
- Add your shower heads MAC Adress into **config.ini** file.
- Edit your MQTT credentials into **config.ini** file.
- Enable/disable file logging and/or MQTT from **config.ini file.

## Running this application

Run the following command:
```
./read_Ampiro_shower.sh
```
Application will start searching for the shower head and when water is turned on this application will connect into the shower head and start streaming data from it.
When  water is turned off, shower  turns off the bluetooth and application disconnects. Application switches back to searching for the shower head to turn on again.

## Running this application automatically
You should make sure this application is always running by placing it into cron.

In Ubuntu/rasbian it's easily done by adding the following line into your crontab.
```
@reboot sleep 20 && /home/pi/amphiro_oras_bluetooth_shower_hub/read_Ampiro_shower.sh
```
This will make sure that application is executed 20 seconds after reboot. (20 sec delay to make sure all the services are up and running.)

# Roadmap

Ideas to be implemented in the future:
- Create "setup application" that will scan and find your Bluetooth shower head and automatically store it's MAC into settings.
- Calculate your daily water consumption and add it into outgoing MQTT-messages

## License
This application is licensed under **[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)**

