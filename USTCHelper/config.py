import os
import json
import base64

config = {
    "in-command": {
        "state": False,
        "config": {}
    },
    "service": {}
}

class ConfigError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ConfigError: {self.text}"

def DumpConfig(stuid, user_config):
    if config["in-command"]["state"]:
        config["in-command"]["config"] = user_config
        return
    if not os.path.exists("conf"):
        os.mkdir("conf")
    with open(f"conf/{stuid}.json", "w") as f:
        json.dump(user_config, f, indent=4)

def LoadConfig(stuid):
    if config["in-command"]["state"]:
        return config["in-command"]["config"]
    try:
        with open(f"conf/{stuid}.json", "r") as f:
            user_config = json.load(f)
    except Exception as e:
        user_config = {}
    return user_config

CONFIG_SERVICE_NAME = "get-config"
config["service"][CONFIG_SERVICE_NAME] = {
    "doc": "获取用户配置",
}

class Config:
    SERVICE_NAME = CONFIG_SERVICE_NAME
    service = config["service"][SERVICE_NAME]
    def __init__(self, stuid, silence=None, params=None, **kwargs):
        self.stuid = stuid
        self.run(silence)

    def run(self, silence=None):
        if config["in-command"]["state"]:
            origin_config = config["in-command"]["config"]
        else:
            user_config = LoadConfig(stuid=self.stuid)
            origin_config = {
                "user_params": user_config["user_params"],
                "password": user_config["password"]
            }
        b64config = base64.b64encode(json.dumps(origin_config).encode()).decode("ASCII")
        if not silence:
            print("b64config:", b64config)
            print("b64config_decode:", json.loads(base64.b64decode(b64config.encode()).decode()))
        return b64config

config["service"][CONFIG_SERVICE_NAME]["entry"] = Config
