#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import sys
import json
import requests
import ssl

from mythic_container.C2ProfileBase import *

client               = None
MythicHost           = None
MythicPort           = None
headers              = None
mqtt_topic           = None
mqtt_topic_mythic    = None
mqtt_topic_taskcheck = None
debug                = False


def _forward_to_mythic(raw: bytes) -> None:
    url = f"http://{MythicHost}:{MythicPort}/agent_message"
    try:
        resp = requests.post(url, data=raw, headers=headers, timeout=15)
        client.publish(mqtt_topic + mqtt_topic_mythic, resp.text, qos=1, retain=False)
    except Exception as e:
        print(f"mqtt: forward error: {e}", file=sys.stderr)


def on_connect(mqtt_client, userdata, flags, rc) -> None:
    if rc == 0:
        mqtt_client.subscribe(mqtt_topic + mqtt_topic_taskcheck, qos=0)
        if debug:
            print(f"mqtt: connected, subscribed to {mqtt_topic + mqtt_topic_taskcheck}")
    else:
        print(f"mqtt: broker connect failed rc={rc}", file=sys.stderr)


def on_disconnect(mqtt_client, userdata, rc) -> None:
    if rc != 0:
        print(f"mqtt: unexpected disconnect rc={rc}", file=sys.stderr)


def on_message(mqtt_client, userdata, msg) -> None:
    try:
        _forward_to_mythic(msg.payload)
    except Exception as e:
        print(f"mqtt: on_message error: {e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        MythicHost = os.environ["MYTHIC_SERVER_HOST"]
        MythicPort = os.environ["MYTHIC_SERVER_PORT"]
        headers    = {"Mythic": "mqtt"}
    except KeyError as e:
        print(f"mqtt: missing env var {e}", file=sys.stderr)
        sys.exit(1)

    with open("config.json") as f:
        cfg = json.load(f)["instances"][0]

    mqtt_server          = cfg["mqtt_server"]
    mqtt_port            = int(cfg["mqtt_port"])
    mqtt_topic           = cfg["mqtt_topic"]
    mqtt_topic_mythic    = cfg["mqtt_mythic"]
    mqtt_topic_taskcheck = cfg["mqtt_taskcheck"]
    mqtt_user            = cfg.get("mqtt_user", "")
    mqtt_pass            = cfg.get("mqtt_pass", "")
    use_ssl         = str(cfg.get("use_ssl", True)).lower() != "false"
    skip_tls_verify = str(cfg.get("skip_tls_verify", True)).lower() != "false"
    use_ws          = str(cfg.get("websockets", False)).lower() == "true"
    debug                = str(cfg.get("debug", False)).lower() == "true"

    if not mqtt_server:
        print("mqtt: mqtt_server is not configured", file=sys.stderr)
        sys.exit(1)

    transport = "websockets" if use_ws else "tcp"

    client = mqtt.Client(transport=transport)

    if use_ssl:
        ctx = ssl.create_default_context()
        if skip_tls_verify:
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE
        client.tls_set_context(ctx)

    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_pass)

    if debug:
        client.enable_logger()

    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(mqtt_server, mqtt_port, keepalive=60)
        client.loop_forever(retry_first_connection=True)
    except Exception as e:
        print(f"mqtt: {e}", file=sys.stderr)
        sys.exit(1)
