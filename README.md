# MQTT C2 Profile
This is a Mythic C2 Profile called mqtt. It provides a way for agents to connect to a intermediary mqtt server in which the C2 Profile also communicates. 
This profile includes:

    Kill Dates
    Sleep Intervals (for the messages within the single websocket connection)
    Support for SSL

The c2 profile has `mythic_container==0.5.12 PyPi` package installed and reports to Mythic as version "3.3".
This repo containes a mqtt listener that will connect to an external mqtt server.  
This allows multiple agents to conenct to the same mqtt server, the Mythic mqtt C2 profile will poll the mqtt server to send commands and receive responses.

## MQTT C2 Workflow
![2025-05-15_22-30](https://github.com/user-attachments/assets/ff594c8b-25fe-4f84-8011-c4dabf7f4cfd)
1. The agent sends a checkin to the pre defined basetopic/checkin topic.
2. The C2 Profile is subscribed to the checkin and output subtopics so it sees the checkin and forwards to Mythic.
3. Mythic responds with tasking and the C2 Profile sends a message to the checkin subtopic with the task received from Mythic
4. As the agent is subscribed to the checkin subtopic, it sees the message and performs the task.
5. After completion of the task the agent sends a message to the output subtopic with the results of said task.
6. The C2 Profile takes the task output from the output topic, and displays it in the Mythic UI.

## How to install an agent in this format within Mythic

Use mythic-cli to install it:
`sudo ./mythic-cli install github https://github.com/grampae/mqtt.git`

See https://docs.mythic-c2.net/installation#installing-agents-c2-profiles for more information
