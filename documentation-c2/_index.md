+++
title = "mqtt"
chapter = false
weight = 5
+++

## Overview

This C2 profile connects to a private MQTT broker and relays messages between MQTT-based agents and the Mythic server. It is designed to work with the styx relay infrastructure — agents connect to public relay VPSes over TLS, relays bridge to the hidden broker over WireGuard, and the profile container connects to that same broker over WireGuard.

### C2 Workflow

{{<mermaid>}}
sequenceDiagram
    participant M as Mythic
    participant Q as MQTT Container
    participant B as Broker
    participant R as Relay VPS
    participant A as Agent
    A ->>+ R: TLS:8883 — agent checkin on mqtt_taskcheck topic
    R ->>+ B: WireGuard bridge — forward
    B ->>+ Q: deliver to styx-listener subscription
    Q ->>+ M: POST /agent_message
    M -->>- Q: tasking response
    Q -->>- B: publish on mqtt_mythic topic (QoS 1)
    B -->>- R: bridge forward
    R -->>- A: deliver tasking
{{< /mermaid >}}

- Agent → broker path: QoS 0 (no replay on reconnect, prevents duplicate task delivery)
- Mythic → agent path: QoS 1 (at-least-once delivery)

---

## Port layout — read this first

The styx broker exposes **two separate listeners** on different ports. Using the wrong port is the most common misconfiguration.

| Port | Who connects | Transport | Netbird policy required |
|------|-------------|-----------|------------------------|
| **8883** | Relay VPSes (bridge to broker) and agents directly | TLS | relay → broker TCP:8883 |
| **1883** | Mythic `mqttclient.py` (this profile) | TLS over WireGuard | mythic-ops → broker TCP:1883 |

**`config.json` must use port `1883`.** Port `8883` is for relay bridges, not for the Mythic listener. If the Netbird policy only permits `1883`, connecting on `8883` will silently time out and Epona will never receive tasking.

---

## Configuration

The profile reads `config.json` on startup. Set these values before starting the container.

```json
{
  "instances": [
    {
      "mqtt_server": "broker.wg.ip",
      "mqtt_port": "1883",
      "mqtt_topic": "epona/",
      "mqtt_mythic": "1",
      "mqtt_taskcheck": "2",
      "mqtt_user": "mythic",
      "mqtt_pass": "your-mqtt-password",
      "use_ssl": true,
      "skip_tls_verify": true,
      "websockets": false,
      "debug": false,
      "payloads": {}
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `mqtt_server` | Broker WireGuard IP or hostname |
| `mqtt_port` | **Must be `1883`** — the broker's Mythic listener port (not the relay port 8883) |
| `mqtt_topic` | Base topic prefix — must match what agents were built with |
| `mqtt_mythic` | Sub-topic for Mythic → agent messages (tasking) |
| `mqtt_taskcheck` | Sub-topic for agent → Mythic messages (checkin, responses) |
| `mqtt_user` | MQTT username for broker auth |
| `mqtt_pass` | MQTT password for broker auth |
| `use_ssl` | `true` to enable TLS on the broker connection |
| `skip_tls_verify` | `true` to accept self-signed broker certificates |
| `websockets` | `true` to use WebSocket transport instead of raw TCP |
| `debug` | `true` to enable paho-mqtt verbose logging |

---

## Profile Parameters

These are baked into the agent binary at build time. They are separate from `config.json`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mqtt_server` | *(required)* | Primary relay hostname or IP — **port 8883**, not the broker |
| `mqtt_server_1..3` | *(empty)* | Failover relay addresses — agent tries each in order |
| `mqtt_port` | `8883` | Relay port agents connect to |
| `use_ssl` | `True` | TLS on relay connection |
| `skip_tls_verify` | `True` | Accept self-signed relay certificates |
| `mqtt_client` | `epona` | Agent MQTT client ID — leave as `epona` to auto-generate a unique ID per build from payload UUID |
| `mqtt_user` | *(empty)* | MQTT username |
| `mqtt_pass` | *(empty)* | MQTT password |
| `mqtt_topic` | `epona/` | Base topic prefix — must match `mqtt_topic` in `config.json` |
| `mqtt_mythic` | `1` | Mythic → agent sub-topic |
| `mqtt_taskcheck` | `2` | Agent → Mythic sub-topic |
| `callback_interval` | `10` | Agent sleep between checkins (seconds) |
| `callback_jitter` | `14` | Jitter percent |
| `killdate` | *(1 year)* | Agent auto-exit date |
| `AESPSK` | `aes256_hmac` | Payload encryption |
| `encrypted_exchange_check` | `True` | RSA key exchange on checkin |
| `websockets` | `False` | WebSocket transport |

---

## OPSEC

- The broker is never internet-exposed — agents connect to relay VPSes, relays bridge to broker over WireGuard.
- All relay addresses (`mqtt_server`, `mqtt_server_1..3`) are ChaCha20-obfuscated at compile time in the Epona agent binary — they do not appear as plaintext strings.
- The `mqtt_topic` base prefix is operator-configurable per operation — no fixed topic string appears in broker logs across engagements.
- Use a different `mqtt_user`/`mqtt_pass` per operation (`broker/add-op.sh`).
- `skip_tls_verify=True` is appropriate for self-signed relay certificates. Set to `False` if using a CA-signed certificate with pinning.
