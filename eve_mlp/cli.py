import os
import sys
import logging
import argparse
import json
from getpass import getpass

from .login import do_login, LoginFailed


log = logging.getLogger(__name__)
config_path = os.path.expanduser("~/.config/eve-mlp.conf")


def load_config():
    try:
        config = json.loads(file(config_path).read())
    except:
        config = {}
    return config


def save_config(config):
    try:
        file(config_path, "w").write(json.dumps(config))
    except:
        pass


def parse_args(args):
    config = load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("--evedir", help="Point to the location of the eve install folder", default=config.get("evedir"))
    parser.add_argument("--username", help="Username to log in with (can be used multiple times)", action="append")
    parser.add_argument("--dry", help="Dry-run (for mlp developers)", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', action="count", default=0)
    args = parser.parse_args(args)

    logging.basicConfig(level=logging.WARNING)
    l2log = logging.getLogger("launcher2")
    l2log.setLevel(logging.WARNING - args.verbose * 10)

    if args.evedir:
        config["evedir"] = args.evedir
        os.chdir(args.evedir)

    if not os.path.exists("bin/ExeFile.exe"):
        logging.error("Need to be run from the eve install dir, or use --evedir")
        return 1

    save_config(config)

    return args


def main(argv=sys.argv):
    args = parse_args(argv[1:])

    usernames = args.username or [raw_input("Username: "), ]
    un2pw = {}
    for username in usernames:
        if len(usernames) == 1:
            password = getpass("Password: ")
        else:
            password = getpass("%s's Password: " % username)
        un2pw[username] = password

    for username, password in un2pw.items():
        try:
            if args.dry:
                print "(Not) Logging in as", username
                print "(Not) Launching eve from", os.getcwd()
            else:
                launch_token = do_login(username, password, args)
                log.info("Launching eve")
                os.system("wine bin/ExeFile.exe /ssoToken=" + launch_token)
        except LoginFailed as e:
            log.error("Login failed: %s", e)
            return 1
