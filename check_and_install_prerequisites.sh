#!/bin/bash

echo "Checking prerequisites..."

echo -n "Checking python3 ..."
pythonInstalled=`dpkg -l python3 |wc -l`
if [ $pythonInstalled -eq "0" ]; then
        echo "Python3 not installed. Installing it."
        sudo apt-get -y install python3
else
        echo " found."
fi

echo -n "Checking pip3 ..."
pipInstalled=`dpkg -l python3-pip |wc -l`
if [ $pipInstalled -eq "0" ]; then
        echo "Python3 pip not installed. Installing it."
        sudo apt-get -y install python3-pip
else
        echo " found."
fi

echo -n "Checking Paho-MQTT (This can take up to 1min) ..."
pahoInstalled=`pip3 list --format=columns |grep paho-mqtt`
if [ -z "$pahoInstalled" ]; then
        echo "Python Paho MQTT library not installed. Installing it."
        sudo pip3 install paho-mqtt
else
        echo " found."
fi

echo -n "Checking BluePy (This can take up to 1min)..."
bluepyInstalled=`pip3 list --format=columns |grep bluepy`
if [ -z "$bluepyInstalled" ]; then
        echo "Python BluePy library not installed. Installing it."
        sudo pip3 install bluepy
else
        echo " found."
fi
