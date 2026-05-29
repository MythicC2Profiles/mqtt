from mythic_container.C2ProfileBase import *
import pathlib
import os

class mqtts(C2Profile):
    name        = "mqtt"
    description = "MQTT C2 profile for relay-based agent communication"
    author      = "@grampae"
    is_p2p           = False
    is_server_routed = False
    server_binary_path = pathlib.Path(".") / "mqtt" / "c2_code" / "mqttclient.py"
    server_folder_path = pathlib.Path(".") / "mqtt" / "c2_code"

    parameters = [
        C2ProfileParameter(
            name="mqtt_server",
            description="Primary MQTT relay hostname or IP",
            default_value="",
            required=True,
        ),
        C2ProfileParameter(
            name="mqtt_server_1",
            description="Failover relay 1 (optional)",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="mqtt_server_2",
            description="Failover relay 2 (optional)",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="mqtt_server_3",
            description="Failover relay 3 (optional)",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="mqtt_port",
            description="MQTT relay port",
            format_string="[0-65535]{1}",
            default_value="8883",
            randomize=False,
            required=True,
        ),
        C2ProfileParameter(
            name="use_ssl",
            description="TLS on the relay connection",
            parameter_type=ParameterType.ChooseOne,
            choices=["True", "False"],
            default_value="True",
            required=True,
        ),
        C2ProfileParameter(
            name="skip_tls_verify",
            description="Accept self-signed relay certificates",
            parameter_type=ParameterType.ChooseOne,
            choices=["True", "False"],
            default_value="True",
            required=True,
        ),
        C2ProfileParameter(
            name="mqtt_client",
            description="MQTT client ID baked into the agent binary — keep as 'epona' to auto-generate a unique ID per build from the payload UUID",
            default_value="epona",
            required=True,
        ),
        C2ProfileParameter(
            name="mqtt_user",
            description="MQTT username",
            default_value="",
            required=False,
        ),
        C2ProfileParameter(
            name="mqtt_pass",
            description="MQTT password",
            default_value="",
            required=False,
            parameter_type=ParameterType.String,
        ),
        C2ProfileParameter(
            name="mqtt_topic",
            description="Base topic for agent tasking",
            default_value="epona/",
            required=True,
        ),
        C2ProfileParameter(
            name="mqtt_mythic",
            description="Mythic→Agent sub-topic",
            format_string="[0-9999]{1}",
            default_value="1",
            randomize=False,
            required=True,
        ),
        C2ProfileParameter(
            name="mqtt_taskcheck",
            description="Agent→Mythic sub-topic",
            format_string="[0-9999]{1}",
            default_value="2",
            randomize=False,
            required=True,
        ),
        C2ProfileParameter(
            name="callback_interval",
            description="Callback interval (seconds)",
            format_string="[0-9999]{1}",
            default_value="10",
            randomize=False,
            required=True,
        ),
        C2ProfileParameter(
            name="callback_jitter",
            description="Callback jitter (%)",
            format_string="[0-9999]{1}",
            default_value="14",
            randomize=False,
            required=True,
        ),
        C2ProfileParameter(
            name="killdate",
            description="Kill date",
            parameter_type=ParameterType.Date,
            default_value=365,
            required=True,
        ),
        C2ProfileParameter(
            name="AESPSK",
            description="Payload encryption",
            default_value="aes256_hmac",
            parameter_type=ParameterType.ChooseOne,
            choices=["aes256_hmac", "none"],
            required=False,
            crypto_type=True,
        ),
        C2ProfileParameter(
            name="encrypted_exchange_check",
            description="Perform RSA key exchange on checkin",
            parameter_type=ParameterType.ChooseOne,
            choices=["True", "False"],
            default_value="True",
            required=True,
        ),
        C2ProfileParameter(
            name="websockets",
            description="Use WebSockets transport",
            parameter_type=ParameterType.ChooseOne,
            choices=["False", "True"],
            default_value="False",
            required=True,
        ),
    ]
