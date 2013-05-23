import os
import json
import hashlib
import logging
import eve_mlp.aes as aes


config_path = os.path.expanduser("~/.config/eve-mlp.conf")
log = logging.getLogger(__name__)


def load_config():
    config = {
        "usernames": [],
        "passwords": {},
    }
    try:
        config.update(json.loads(file(config_path).read()))
    except:
        log.debug("Couldn't load config file:", exc_info=True)
    return config


def save_config(config):
    try:
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        file(config_path, "w").write(json.dumps(config, indent=4))
    except:
        log.debug("Couldn't save config file:", exc_info=True)


def encrypt(cleartext, key):
    moo = aes.AESModeOfOperation()

    cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
    iv = [ord(x) for x in os.urandom(16)]

    mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
    return json.dumps([mode, orig_len, ciph, iv]).replace(" ", "")


def decrypt(data, key):
    moo = aes.AESModeOfOperation()

    cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
    mode, orig_len, ciph, iv = json.loads(data)

    cleartext = moo.decrypt(ciph, orig_len, mode, cypherkey, moo.aes.keySize["SIZE_128"], iv)
    return cleartext


if __name__ == "__main__":
    encrypted = encrypt("Hello!", "password")
    print "Encrypted: %r" % encrypted
    decrypted = decrypt(encrypted, "password")
    print "Decrypted: %r" % decrypted
