#!/usr/bin/python3
#import necessary libraries
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import sys
import time
import RPi.GPIO as GPIO
import seeed_dht
import logging
from dotenv import dotenv_values

#initialise DHT22 temperature/humidity sensor device, 22 refers to sensor type and 4 refers to GPIO pin for data connection
sensor = seeed_dht.DHT("22", 4) 
#defining humidity and temperature variables for reading from sensor
humi, temp = sensor.read() 

#load MQTT configuration values from .env file
config = dotenv_values(".env")

#configure Logging
logging.basicConfig(level=logging.INFO)

# Define event callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connection Result: " + str(rc))

def on_publish(client, obj, mid):
    logging.info("Message Sent ID: " + str(mid))

mqttc = mqtt.Client(client_id=config["clientId"])

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# parse mqtt url for connection details
url_str = 'mqtt://mqtt3.thingspeak.com:8883'
print(url_str)
url = urlparse(url_str)
base_topic = url.path[1:]

# Configure MQTT client with user name and password
mqttc.username_pw_set(config["username"], config["password"])
# Load CA certificate for Transport Layer Security
mqttc.tls_set("./broker.thingspeak.crt")

#Connect to MQTT Broker
mqttc.connect(url.hostname, url.port)
mqttc.loop_start()

#Set Thingspeak Channel to publish to
topic = "channels/"+config["channelId"]+"/publish"

# Publish a message to temp every 16 seconds via indefinite loop
while True:
    try:
        print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp)) #print the sensor type, temperature, and humidity values in the console
        payload=f"field1={temp}&field2={humi}" #define fields (temperature and humidity) for data transfer to MQTT Broker
        mqttc.publish(topic, payload) #publish to MQTT broker
        time.sleep(int(config["transmissionInterval"])) #wait for defined interval (16 seconds) before repeating loop
    except: #exception for not repeating loop
        logging.info('Interrupted') #log an interuption to the loop