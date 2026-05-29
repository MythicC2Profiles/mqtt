# mqtt

Mythic C2 profile for MQTT-based agent communication over the styx relay infrastructure.

---

## Infrastructure topology

```
Internet
  │  port 8883 (TLS)
  ▼
Relay VPS(es)       ← public-facing, ephemeral, one or more
  │  WireGuard mesh (private)
  ▼
MQTT Broker         ← never internet-exposed
  │  WireGuard  port 1883
  ▼
Mythic server       ← connects to broker, never to relays
```

Agents connect to relays over TLS on port **8883**. Relays bridge all traffic to the hidden broker over WireGuard. The Mythic listener (`mqttclient.py`) connects to the broker on port **1883** over WireGuard — a separate listener that relay bridges never touch. A burned relay does not expose the broker or Mythic.

Agent failover: up to four relay hostnames baked into the binary at build time (`mqtt_server` + `mqtt_server_1..3`). The agent tries each in order on connection failure.

---

## Port layout

| Port | Used by | Notes |
|------|---------|-------|
| **8883** | Relay VPS bridges, agents | TLS; never opened to Mythic |
| **1883** | `mqttclient.py` (this profile) | TLS over WireGuard; Netbird policy must permit mythic → broker TCP:1883 |

**`config.json` must use port `1883`.** Connecting on `8883` will time out silently if the Netbird policy only permits `1883`.

---

## Topic layout

```
<mqtt_topic><mqtt_taskcheck>    ← agent → Mythic (checkins, responses)
<mqtt_topic><mqtt_mythic>       ← Mythic → agent (tasking)
```

All topic components are operator-configurable — no fixed strings appear in broker logs.

### QoS

| Channel | QoS | Reason |
|---------|-----|--------|
| Agent → Mythic (taskcheck) | 0 | No replay on reconnect — prevents duplicate delivery |
| Mythic → agent (mythic) | 1 | At-least-once delivery to broker |

---

## config.json

The listener reads this file on startup. Credentials and broker address go here — this file is **not** committed with live values.

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

---

## C2 profile parameters

Set in the Mythic UI at payload build time. Baked into the agent binary — separate from `config.json`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mqtt_server` | *(required)* | Primary relay hostname or IP — port **8883** |
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

## Broker ACL

```
# mosquitto example

# Mythic listener — full access on its topic prefix
user mythic
topic readwrite #

# Epona agent — scoped to its own topic prefix
user epona-<op>
topic readwrite epona/#
```

---

## OPSEC

- The broker is never internet-exposed. Agents only ever reach relay VPSes.
- Relay addresses are ChaCha20-obfuscated at compile time in the agent binary — they do not appear as plaintext strings.
- `mqtt_topic` is operator-configurable per operation — no fixed topic string appears across broker logs.
- Use a different `mqtt_user`/`mqtt_pass` per operation (`broker/add-op.sh` in the styx repo).
- `skip_tls_verify=True` is appropriate for self-signed relay certificates. Set to `False` with a CA-signed cert for pinning.
