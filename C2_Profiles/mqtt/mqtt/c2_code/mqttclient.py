#! /usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import sys
import json
import requests
import random
from mythic_container.C2ProfileBase import *

# Send agent messages to Mythic
def mythic_c2_agent_message(message):
	MythicReceive = "http://"+MythicHost+":"+MythicPort+"/agent_message"
	response = requests.post(MythicReceive, data=message, headers=headers)
	send_mqtt_message(mqtt_topic+mqtt_topic_mythic, response.text)
# Function to process messages received from MQTT clients
def on_message(client, userdata, msg):
	try:
		payload = msg.payload.decode('utf-8')
		mythic_c2_agent_message(payload)

	except Exception as e:
		print(f"Error processing message: {str(e)}")

# Function to send a message to the MQTT topic
def send_mqtt_message(topic, message):
	result = client.publish(topic, message)
	if result.rc == mqtt.MQTT_ERR_SUCCESS:
		pass
	else:
		print(f"Failed to send message to {topic}")


# MQTT setup
def on_connect(client, userdata, flags, rc):
	print(f"Connected to MQTT broker with result code {rc}")
	# Subscribe to the base topic plus agentout
	client.subscribe(mqtt_topic+mqtt_topic_taskcheck)


if __name__ == "__main__":

	print("Opening config and starting instances...")
	# basic mapping of the general endpoints to the real endpoints
	try:
		MythicHost = os.environ['MYTHIC_SERVER_HOST']
		MythicPort = os.environ['MYTHIC_SERVER_PORT']
		headers = {
		'Mythic' : 'mqtt'
			}
	except Exception as e:
		print("failed to find MYTHIC_ADDRESS environment variable" + e)
		sys.exit(1)

	try:
		# Load config.json file and assign variables
		
		with open('config.json', 'r') as config_file:
			config_data = json.load(config_file)
			mqtt_server = config_data['instances'][0]['mqtt_server']
			mqtt_port = int(config_data['instances'][0]['mqtt_port'])
			mqtt_topic = config_data['instances'][0]['mqtt_topic']
			mqtt_topic_mythic = config_data['instances'][0]['mqtt_mythic']
			mqtt_topic_taskcheck = config_data['instances'][0]['mqtt_taskcheck']
			mqtt_user = config_data['instances'][0]['mqtt_user']
			mqtt_pass = config_data['instances'][0]['mqtt_pass']
			use_ssl = config_data['instances'][0]['use_ssl']
			debug = config_data['instances'][0]['debug']
			if debug:
				print("Debugging statements are enabled. This gives more context, but might be a performance hit")
			else:
				print("Debugging statements are disabled")
	except Exception as e:
		print(str(e))
	client = mqtt.Client()
	
	try:
		if use_ssl == True:
			client.tls_set()
		if mqtt_user:
			client.username_pw_set(mqtt_user,mqtt_pass)
		client.on_connect = on_connect
		client.on_message = on_message
		
		# Connect to the MQTT broker and start the loop
		client.connect(mqtt_server, mqtt_port, 60)	
		client.loop_forever()
	except Exception as e:
		print("Error :"+str(e))
	
