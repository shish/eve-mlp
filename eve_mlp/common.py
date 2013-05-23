import os
import json


config_path = os.path.expanduser("~/.config/eve-mlp.conf")


def load_config():
    config = {
        "usernames": [],
        "passwords": {},
    }
    try:
        config.update(json.loads(file(config_path).read()))
    except:
        pass
    return config


def save_config(config):
    try:
        file(config_path, "w").write(json.dumps(config, indent=4))
    except:
        pass


def encrypt(data, key):
    return data


def decrypt(data, key):
    return data
