# mqtt C2 Profile

This repo containes a mqtt listener that will connect to an external mqtt server.  
This allows multiple agents to conenct to the same mqtt server, the Mythic mqtt C2 profile will poll the mqtt server to send commands and receive responses.

```
sudo ./mythic-cli install github <url to your agent> [optional branch name]
```

There are quite a few free cloud based mqtt server options out there as well as self hosted ones like Mosquitto etc.
