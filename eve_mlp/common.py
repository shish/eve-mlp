import os
import json


config_path = os.path.expanduser("~/.config/eve-mlp.conf")


def load_config():
    try:
        config = json.loads(file(config_path).read())
    except:
        config = {}
    return config


def save_config(config):
    try:
        file(config_path, "w").write(json.dumps(config, indent=4))
    except:
        pass
