# mqtt

Mythic C2 profile for MQTT-based agent communication. Supports persistent broker sessions, dual-channel QoS, and optional sensor event ingestion for ouroboros telemetry.

---

## Infrastructure topology

```
Internet
  │  port 8883 (TLS)
  ▼
Relay VPS(es)   ← public-facing, one or more
  │  WireGuard mesh (private)
  ▼
MQTT Broker     ← never internet-exposed
  │  WireGuard
  ▼
Mythic server   ← air-gapped from internet
```

Agents connect to relays over TLS. Relays bridge to the broker over WireGuard. Mythic connects to the broker over WireGuard. A blocked or burned relay does not expose the broker or Mythic.

Agent failover: up to four relay hostnames baked into the binary (`mqtt_server` + `mqtt_server_1..3`). The agent tries each in order; if one fails it moves to the next.

---

## Topic layout

```
<base_topic><recv_subtopic>    ← tasking: Mythic → agent
<base_topic><send_subtopic>    ← responses: agent → Mythic
<sensor_topic>/<cb_uuid>/<event_type>   ← sensor events (QoS 1 + RETAIN)
```

All topic components are operator-configurable — no fixed strings appear in broker logs.

### QoS split

| Channel | QoS | Reason |
|---------|-----|--------|
| Agent tasking (recv) | 0 | No replay on reconnect — prevents duplicate task delivery |
| Agent responses (send) | 1 | At-least-once delivery to Mythic |
| Sensor events | 1 | Persistent session queues events published while offline |

### Persistent vs clean sessions

| Agent | `clean_session` | Reason |
|-------|-----------------|--------|
| ouroboros | `False` | Broker queues missed sensor events while listener is offline |
| epona (stateless) | `True` | No session state needed; avoids stale message buildup |

---

## Sensor event ingestion

When `sensor_ingestion=True` and a message arrives on `<sensor_topic>/#`, the listener:

1. Parses `<sensor_topic>/<callback_uuid>/<event_type>` from the topic
2. Looks up the Mythic callback for `callback_uuid`
3. Creates a Mythic task result attached to the active `stream` task for that callback
4. The event appears in the Mythic UI as streaming output

This happens in a background thread so it does not block agent message processing.

---

## C2 profile parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mqtt_server` | *(required)* | Primary relay hostname or IP |
| `mqtt_server_1..3` | `` | Failover relays (optional) |
| `mqtt_port` | `8883` | Relay port |
| `use_ssl` | `True` | Enable TLS on relay connection |
| `skip_tls_verify` | `True` | Accept self-signed relay certificates |
| `clean_session` | `False` | `False` = persistent sessions (ouroboros); `True` = stateless (epona) |
| `sensor_ingestion` | `True` | Subscribe to `sensor_topic/#` and forward events to Mythic |
| `sensor_topic` | `telemetry` | Topic prefix for sensor events — must match `mqtt_sensor_prefix` baked into agent binary |
| `mqtt_client` | `styx-listener` | Listener client ID — only relevant for broker ACLs |
| `mqtt_user` | `` | MQTT username |
| `mqtt_pass` | `` | MQTT password |
| `mqtt_topic` | `epona/` | Base topic prefix for agent channels |
| `mqtt_mythic` | `1` | Recv sub-topic (Mythic → agent) |
| `mqtt_taskcheck` | `2` | Send sub-topic (agent → Mythic) |
| `callback_interval` | `10` | Agent sleep between exchanges (seconds) |
| `callback_jitter` | `14` | Jitter percent |
| `killdate` | *(1 year)* | Kill date |
| `AESPSK` | *(Mythic-managed)* | AES-256 encryption key pair |
| `encrypted_exchange_check` | `True` | RSA key exchange on checkin |
| `websockets` | `False` | Use WebSockets transport |

---

## Opsec: sensor topic

The `sensor_topic` parameter controls what the listener subscribes to. It must match the `mqtt_sensor_prefix` build parameter baked into the ouroboros binary. Set both to an operator-chosen value per operation — the default `telemetry` should be changed. This ensures no fixed topic string appears consistently across broker logs.

---

## Broker ACL recommendations

```
# mosquitto example

# mqtt listener — full access
user styx-listener
topic readwrite #

# ouroboros agent — write only to sensor topic and its own channel
user ouroboros-<uuid>
topic write telemetry/#
topic readwrite <base_topic>/#
```

---

## Relay TLS

The relay presents a certificate on port 8883. With `skip_tls_verify=True` (default), agents and the listener accept any certificate — appropriate for self-signed. Set `skip_tls_verify=False` and provision a proper certificate for pinning.

---

## Directory layout

```
mqtt/
├─ README.md
└─ C2_Profiles/mqtt/mqtt/
    ├─ c2_code/
    │   └─ mqttclient.py   # paho client, sensor ingestion, QoS split
    └─ c2_functions/
        └─ mqtt.py         # C2Profile class, all parameter definitions
```
