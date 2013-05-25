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


class LaunchConfig(object):
    """
    Holds the settings for a given launch configuration.

    Takes another LaunchConfig as a base, so that we can have one "default"
    account which sets the common things like where the game is installed,
    then seperate sub-launches inheriting from that which store the
    usernames & passwords.
    """

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
        return "LaunchConfig(%r)" % self._confname

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
    """
    The root data structure that holds all the launches and app settings;
    most of the parts of the app will have a reference to this structure,
    and they work together to modify it according to the user's will.
    """

    def __init__(self):
        self.defaults = LaunchConfig(None, {
            "confname": None,
            "username": None,
            "password": None,
            "gamepath": ".",
            "serverid": "tranquility",
        })
        self.launches = []
        self.settings = {
            "remember-passwords": False,
            "start-tray": False,
        }
        self.master_password = None

    def load(self):
        try:
            config = json.loads(file(config_path).read())

            self.defaults.gamepath = config.get("defaults", {}).get("gamepath")
            self.defaults.serverid = config.get("defaults", {}).get("serverid")

            self.launches = []
            for launch_config_data in config["accounts"]:
                self.launches.append(LaunchConfig(self.defaults, launch_config_data))

            self.settings.update(config["settings"])
        except:
            log.debug("Couldn't load config file:", exc_info=True)

    def save(self):
        config = {
            "defaults": self.defaults.__json__(),
            "accounts": [a.__json__() for a in self.launches],
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
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = decrypt(launch_config.password, self.master_password)
        else:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = None

    def encrypt_passwords(self):
        if self.settings["remember-passwords"]:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = encrypt(launch_config.password, self.master_password)
        else:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = None


def encrypt(cleartext, key):
    try:
        moo = aes.AESModeOfOperation()

        cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
        iv = [ord(x) for x in os.urandom(16)]

        mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
        return json.dumps([mode, orig_len, ciph, iv]).replace(" ", "")
    except Exception as e:
        log.error("Error encrypting data: %s", e)
        return None


def decrypt(data, key):
    try:
        moo = aes.AESModeOfOperation()

        cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
        mode, orig_len, ciph, iv = json.loads(data)

        cleartext = moo.decrypt(ciph, orig_len, mode, cypherkey, moo.aes.keySize["SIZE_128"], iv)
        return cleartext
    except Exception as e:
        log.error("Error decrypting data: %s", e)
        return None


class LaunchFailed(Exception):
    pass


def launch(config, launch_config, launch_token):
    log.info("Launching eve")

    if not os.path.exists(os.path.join(launch_config.gamepath, "bin", "ExeFile.exe")):
        raise LaunchFailed("Can't find bin/ExeFile.exe, is the game folder set correctly?")

    cmd = []

    # platform specific pre-binary bits
    if config.settings.get("dry"):
        cmd.append("echo")
    if platform.system() == "Linux":
        cmd.append("wine")

    # run the app
    cmd.append('"' + os.path.join(launch_config.gamepath, "bin", "ExeFile.exe") + '"')
    if launch_token:
        cmd.append("/ssoToken=" + launch_token)
    cmd.append("/noconsole")

    # app flags
    if launch_config.serverid == "singularity":
        cmd.append("/server:Singularity")

    # go!
    return subprocess.Popen(" ".join(cmd), shell=True)
