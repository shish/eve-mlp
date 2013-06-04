import os
import json
import hashlib
import logging
import subprocess
import platform
import eve_mlp.aes as aes


config_path = os.path.expanduser("~/.config/eve-mlp.conf")
log = logging.getLogger(__name__)


class LaunchConfig(dict):
    """
    Holds the settings for a given launch configuration.

    Takes another LaunchConfig as a base, so that we can have one "default"
    account which sets the common things like where the game is installed,
    then seperate sub-launches inheriting from that which store the
    usernames & passwords.
    """

    def __init__(self, base=None, custom={}):
        defaults = {
            "confname": None,
            "username": None,
            "password": None,
            "gamepath": None,
            "serverid": None,
            "selected": None,
            "console": None,
            "winecmd": None,
            "wineflags": None,
        }
        defaults.update(custom)
        dict.__init__(self, defaults)

        self.base = base
        self._initialised = True

    def __json__(self):
        return self  # we are a dict already \o/

    def __str__(self):
        return "LaunchConfig(%r)" % self.confname

    def __getattr__(self, attr):
        local = False
        if attr[0] == "_":
            attr = attr[1:]
            local = True

        try:
            if self.__getitem__(attr) != None:
                return self.__getitem__(attr)
            if self.base and not local:
                return self.base.__getitem__(attr)
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if '_initialised' not in self.__dict__:  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, attr, value)

        elif attr in self.__dict__:       # any normal attributes are handled normally
            dict.__setattr__(self, attr, value)
        else:
            self.__setitem__(attr, value)


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
            "selected": False,
            "console": False,
            "winecmd": "wine",
            "wineflags": None,
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

        if not self.launches:
            self.launches.append(LaunchConfig(self.defaults, {"confname": "Main Setup"}))

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
                    launch_config.password = decrypt(launch_config.password, self.master_password, pad=True).decode("utf8")
        else:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = None

    def encrypt_passwords(self):
        if self.settings["remember-passwords"]:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = encrypt(launch_config.password.encode("utf8"), self.master_password, pad=True)
        else:
            for launch_config in self.launches:
                if launch_config.password:
                    launch_config.password = None


def encrypt(cleartext, key, text=False, pad=False):
    try:
        moo = aes.AESModeOfOperation()

        if pad:
            cleartext = cleartext + chr(0) + os.urandom(32 - (len(cleartext) + 1) % 32)
        cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
        iv = [ord(x) for x in os.urandom(16)]

        mode, orig_len, ciph = moo.encrypt(cleartext, moo.modeOfOperation["CBC"], cypherkey, moo.aes.keySize["SIZE_128"], iv)
        return json.dumps([mode, orig_len, ciph, iv]).replace(" ", "")
    except Exception as e:
        log.error("Error encrypting data: %s", e)
        return None


def decrypt(data, key, text=False, pad=False):
    try:
        moo = aes.AESModeOfOperation()

        cypherkey = [ord(x) for x in hashlib.md5(key).digest()]
        mode, orig_len, ciph, iv = json.loads(data)

        cleartext = moo.decrypt(ciph, orig_len, mode, cypherkey, moo.aes.keySize["SIZE_128"], iv)

        if pad:
            cleartext = cleartext.partition("\x00")[0]

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
        cmd.append(launch_config.winecmd)
        if launch_config.wineflags:
            cmd.append(launch_config.wineflags)

    # run the app
    cmd.append('"' + os.path.join(launch_config.gamepath, "bin", "ExeFile.exe") + '"')
    if launch_token:
        cmd.append("/ssoToken=" + launch_token)

    # app flags
    if launch_config.console:
        cmd.append("/console")
    else:
        cmd.append("/noconsole")

    if launch_config.serverid == "singularity":
        cmd.append("/server:Singularity")

    # go!
    return subprocess.Popen(" ".join(cmd), shell=True)
