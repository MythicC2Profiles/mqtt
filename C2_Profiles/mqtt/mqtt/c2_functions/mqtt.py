from mythic_container.C2ProfileBase import *
import pathlib
import os

class mqtts(C2Profile):
	name = "mqtt"
	description = "Uses external MQTT server to communicate with agents"
	author = "@grampae"
	is_p2p = False
	is_server_routed = False
	server_binary_path = pathlib.Path(".") / "mqtt" / "c2_code" / "mqttclient.py"
	server_folder_path = pathlib.Path(".") / "mqtt" / "c2_code"
	parameters = [
		C2ProfileParameter(
			name="mqtt_server",
			description="External MQTT hostname or IP address to communicate with",
			default_value="eg.example.com",
			required=True,
		),
		C2ProfileParameter(
			name="mqtt_port",
			description="External MQTT port number",
			format_string="[0-65535]{1}",
			default_value="8883",
			randomize=False,
			required=True,
		),
		C2ProfileParameter(
			name="use_ssl",
			description="Does the mqtt server use SSL?",
			default_value="True",
			required=True,
		),
		C2ProfileParameter(
			name="mqtt_client",
			description="MQTT client ID",
			default_value="broomhilda",
			required=True,
		),
		C2ProfileParameter(
			name="mqtt_user",
			description="MQTT server Username",
			default_value="",
			required=False,
		),
		C2ProfileParameter(
			name="mqtt_pass",
			description="MQTT server Password",
			default_value="",
			required=False,
		),
		C2ProfileParameter(
			name="mqtt_topic",
			description="Base MQTT topic",
			default_value="billbradley/",
			required=True,
		),
		C2ProfileParameter(
			name="mqtt_mythic",
			description="Mqtt Mythic response sub-topic",
			format_string="[0-9999]{1}",
			default_value="1",
			randomize=False,
			required=True,
		),
		C2ProfileParameter(
			name="mqtt_taskcheck",
			description="Mqtt Agent tasking and checkin sub-topic",
			format_string="[0-9999]{1}",
			default_value="2",
			randomize=False,
			required=True,
		),
		C2ProfileParameter(
			name="callback_interval",
			description="Callback Interval",
			format_string="[0-9999]{1}",
			default_value="10",
			randomize=False,
			required=True,
		),
		C2ProfileParameter(
			name="callback_jitter",
			description="Callback Jitter",
			format_string="[0-9999]{1}",
			default_value="14",
			randomize=False,
			required=True,
		),
		C2ProfileParameter(
			name="killdate",
			description="Kill Date",
			parameter_type=ParameterType.Date,
			default_value=365,
			required=True,
		),
        C2ProfileParameter(
            name="AESPSK",
            description="Crypto type",
            default_value="aes256_hmac",
            parameter_type=ParameterType.ChooseOne,
            choices=["aes256_hmac", "none"],
            required=False,
            crypto_type=True
        ),
		C2ProfileParameter(
			name="encrypted_exchange_check",
			description="Perform Key Exchange",
			default_value="True",
			required=True,
		),
		C2ProfileParameter(
			name="websockets",
			description="Does the MQTT server use Websockets?",
			default_value="False",
			required=True,
		)
	]

