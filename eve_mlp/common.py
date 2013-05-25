import os
import json
import hashlib
import logging
import subprocess
import platform
import eve_mlp.aes as aes


__version__ = "0.2.3"


config_path = os.path.expanduser("~/.config/eve-mlp.conf")
log = logging.getLogger(__name__)


class Account(object):
    attrs = ["confname", "username", "password", "gamepath", "serverid"]
        
    def __init__(self, base, custom):
        self.base = base
        for attr in self.attrs:
            setattr(self, "_"+attr, custom.get(attr))

    def __json__(self):
        d = {}
        for attr in self.attrs:
            d[attr] = getattr(self, "_"+attr)
        return d

    def __str__(self):
        return "Account(%r)" % self._confname

    @property
    def confname(self):
        if self._confname:
            return self._confname
        if self.base:
            return self.base._confname

    @confname.setter
    def confname(self, value):
        self._confname = value

    @property
    def username(self):
        if self._username:
            return self._username
        if self.base:
            return self.base._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        if self._password:
            return self._password
        if self.base:
            return self.base._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def gamepath(self):
        if self._gamepath:
            return self._gamepath
        if self.base:
            return self.base._gamepath

    @gamepath.setter
    def gamepath(self, value):
        self._gamepath = value

    @property
    def serverid(self):
        if self._serverid:
            return self._serverid
        if self.base:
            return self.base._serverid

    @serverid.setter
    def serverid(self, value):
        self._serverid = value


class Config(object):
    def __init__(self):
        self.defaults = Account(None, {})
        self.accounts = []
        self.settings = {}
        self.master_password = None

    def load(self):
        config = {
            "defaults": {
                "confname": None,
                "username": None,
                "password": None,
                "gamepath": ".",
                "serverid": "tranquility",
            },
            "accounts": [],
            "settings": {
                "remember-passwords": False,
            },
        }
        try:
            config.update(json.loads(file(config_path).read()))
        except:
            log.debug("Couldn't load config file:", exc_info=True)
            
        self.defaults = Account(None, config["defaults"])
        self.accounts = []
        for acct_data in config["accounts"]:
            self.accounts.append(Account(self.defaults, acct_data))
        self.settings = config["settings"]

    def save(self):
        config = {
            "defaults": self.defaults.__json__(),
            "accounts": [a.__json__() for a in self.accounts],
            "settings": self.settings
        }
        try:
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            file(config_path, "w").write(json.dumps(config, indent=4))
        except:
            log.debug("Couldn't save config file:", exc_info=True)

    def decrypt_passwords(self):
        if self.settings["remember-passwords"]:
            for acct in self.accounts:
                if acct.password:
                    acct.password = decrypt(acct.password, self.master_password)
        else:
            for acct in self.accounts:
                if acct.password:
                    acct.password = None

    def encrypt_passwords(self):
        if self.settings["remember-passwords"]:
            for acct in self.accounts:
                if acct.password:
                    try:
                        acct.password = encrypt(acct.password, self.master_password)
                    except Exception:
                        acct.password = None
        else:
            for acct in self.accounts:
                if acct.password:
                    acct.password = None


def encrypt(cleartext, key):
    moo = aes.AESModeOfOperation()

    cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
    iv = [ord(x) for x in os.urandom(16)]

    mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
    return json.dumps([mode, orig_len, ciph, iv]).replace(" ", "")


def decrypt(data, key):
    try:
        moo = aes.AESModeOfOperation()

        cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
        mode, orig_len, ciph, iv = json.loads(data)

        cleartext = moo.decrypt(ciph, orig_len, mode, cypherkey, moo.aes.keySize["SIZE_128"], iv)
        return cleartext
    except Exception as e:
        log.error("Error decrypting password: %s", e)
        return None


class LaunchFailed(Exception):
    pass


def launch(config, account, launch_token):
    log.info("Launching eve")
    
    if not os.path.exists(os.path.join(account.gamepath, "bin", "ExeFile.exe")):
        raise LaunchFailed("Can't find bin/ExeFile.exe, is the game folder set correctly?")

    cmd = []

    # platform specific pre-binary bits
    if config.settings.get("dry"):
        cmd.append("echo")
    if platform.system() == "Linux":
        cmd.append("wine")

    # run the app
    cmd.append('"' + os.path.join(account.gamepath, "bin", "ExeFile.exe") + '"')
    if launch_token:
        cmd.append("/ssoToken=" + launch_token)
    cmd.append("/noconsole")

    # app flags
    if account.serverid == "singularity":
        cmd.append("/server:Singularity")

    # go!
    return subprocess.Popen(" ".join(cmd), shell=True)
