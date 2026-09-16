+++
title = "mqtt"
chapter = false
weight = 5
+++

## Overview
This C2 profile consists of a MQTT client which sends and receives messages to a MQTT broker, thereby communicating tasks and output between MQTT agents and the C2 profile container, where messages are then forwarded to Mythic's API. The C2 Profile container acts as a proxy between agents and the Mythic server itself.

Agents will communicate on specified server and topics, which this C2 profile is meant to also communicate on.

### C2 Workflow
{{<mermaid>}}
sequenceDiagram
    participant M as Mythic
    participant Q as MQTT Container
    participant A as Agent
    A ->>+ Q: receive checkin message on mqtt_taskcheck topic
    Q ->>+ M: forward request to Mythic
    M -->>- Q: reply with tasking
    Q -->>- A: publish tasking message on mqtt_mythic topic
{{< /mermaid >}}
Legend:

- Solid line is a new connection
- Dotted line is a message within that connection

## Configuration Options
The profile reads a `config.json` file which will be used to set the connection and topic values.

```JSON
{
  "instances": [
    {
      "mqtt_server": "mqtt.broker.com",
      "mqtt_port": "8883",
      "mqtt_topic": "billbradley/",
      "mqtt_mythic": "1",
      "mqtt_taskcheck": "2",
      "mqtt_user": "",
      "mqtt_pass": "",
      "debug": false,
      "use_ssl": true,
      "payloads": {}
    }
  ]
}

```


- mqtt_server -> The MQTT server that the C2 profile and agent will connect to.
- mqtt_port -> The port of the MQTT server.
- mqtt_topic -> The base topic that will house the mqtt_mythic and mqtt_taskcheck subtopics.
- mqtt_mythic -> The subtopic that Mythic uses to send tasks.
- mqtt_taskcheck -> The subtopic that an MQTT agent will use to checkin to.
- mqtt_user -> MQTT username of the mqtt_server (can be blank if using public MQTT server)
- mqtt_pass -> MQTT password of the mqtt_server (can be blank if using public MQTT server)
- debug -> Set debug with true or false
- use_ssl -> Set if mqtt_server uses SSL with true or false


### Profile Options
#### Base MQTT topic	
The base topic that will be used on the MQTT server.
#### Callback Interval	
A number to indicate how many seconds the agent should wait in between tasking requests.
#### Callback Jitter	
Percentage of jitter effect for callback interval.
#### Crypto type	
Indicate if you want to use no crypto (i.e. plaintext) or if you want to use Mythic's aes256_hmac. Using no crypto is really helpful for agent development so that it's easier to see messages and get started faster, but for actual operations you should leave the default to aes256_hmac.
#### Does the mqtt server use SSL?	
If the MQTT server uses SSL set to True, otherwise False.
#### External MQTT hostname or IP address to communicate with	
The hostname of the MQTT server in which communications will be handled.
#### External MQTT port number	
The port number in which the MQTT server uses.
#### Kill Date	
Date for the agent to automatically exit, typically the after an assessment is finished.
#### Mqtt Agent tasking and checkin sub-topic	
A subtopic which will be used to send checkin messages to Mythic
#### MQTT client ID	
A client ID which will be used on the MQTT server.
#### Mqtt Mythic response sub-topic	
A subtopic which will be used to receive messages from Mythic
#### MQTT server Password	
If you need to authenticate to the MQTT server, specify the password here.
#### MQTT server Username	
If you need to authenticate to the MQTT server, specify the username here.
Perform Key Exchange
#### crypto type
Indicate if you want to use no crypto (i.e. plaintext) or if you want to use Mythic's aes256_hmac. Using no crypto is really helpful for agent development so that it's easier to see messages and get started faster, but for actual operations you should leave the default to aes256_hmac.

## OPSEC

This profile doesn't do any randomization of network components outside of allowing operators to specify internals/jitter. Public MQTT servers are great for developing agents however they should be avoided for production use.  There are a few free and paid cloud alternatives in which you can set up a private MQTT server with defined users and acls.


