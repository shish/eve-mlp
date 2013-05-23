import os
import json
import hashlib
import eve_mlp.aes as aes


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


def encrypt(cleartext, key):
    moo = aes.AESModeOfOperation()

    cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
    iv = [ord(x) for x in os.urandom(16)]

    mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
    return [mode, orig_len, ciph, iv]


def decrypt(data, key):
    moo = aes.AESModeOfOperation()

    cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
    mode, orig_len, ciph, iv = data

    cleartext = moo.decrypt(ciph, orig_len, mode, cypherkey, moo.aes.keySize["SIZE_128"], iv)
    return cleartext


if __name__ == "__main__":
    encrypted = encrypt("Hello!", "password")
    print "Encrypted:", encrypted
    decrypted = decrypt(encrypted, "password")
    print "Decrypted:", decrypted
