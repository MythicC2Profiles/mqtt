# mqtt C2 Profile and medusa-mqtt Agent

This repo containes a mqtt listener that will connect to an external mqtt server in the C2_Profiles directory.  
This repo also contains a modified version of the medusa agent which can communicate over mqtt in the Payload_Type directory.

- Oct 8th 2024, updated to convert all medusa capabilities such as download, load etc to communicate over mqtt instead of calling http post functions.

```
sudo ./mythic-cli install github <url to your agent> [optional branch name]
```
