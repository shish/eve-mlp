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
        file(config_path, "w").write(json.dumps(config, indent=4))
    except:
        pass


def parse_args(args, config):
    parser = argparse.ArgumentParser()
    parser.add_argument("--evedir", help="Point to the location of the eve install folder (Remembered across runs)", default=config.get("evedir"), metavar="DIR")
    parser.add_argument("--singularitydir", help="Point to the location of the singularity install folder (Remembered across runs)", default=config.get("singularitydir"), metavar="DIR")
    parser.add_argument("--username", help="Username to log in with (Can be used multiple times, remembered across runs)", dest="usernames", action="append", default=config.get("usernames"), metavar="NAME")
    parser.add_argument("--singularity", help="Launch singularity instead of tranquility", default=False, action="store_true")
    parser.add_argument("--dry", help="Dry-run (for MLP developers)", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="Be more verbose (use more -v's for more verbosity)", action="count", default=0)
    args = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)19.19s %(levelname)4.4s %(message)s")
    module_log = logging.getLogger("eve_mlp")
    module_log.setLevel(logging.WARNING - args.verbose * 10)

    # update remembered config
    if args.evedir:
        config["evedir"] = args.evedir

    if args.singularitydir:
        config["singularitydir"] = args.singularitydir

    if args.usernames:
        config["usernames"] = args.usernames

    # move to the configured directory
    if args.singularity:
        if config.get("singularitydir"):
            os.chdir(config["singularitydir"])
    else:
        if config.get("evedir"):
            os.chdir(config["evedir"])

    if not os.path.exists("bin/ExeFile.exe"):
        logging.error("Need to be run from the eve install dir, or use --evedir")
        return 1

    # return
    return args


def log_config(args, config):
    log.info("MLP Software:")
    log.info("  Verbosity       : %s", args.verbose)
    log.info("  Launching       : %s", "Singularity" if args.singularity else "EVE")
    log.info("")

    log.info("Eve Software:")
    log.info("  Eve dir         : %s", args.evedir)
    log.info("  Singularity dir : %s", args.singularitydir)
    log.info("")

    log.info("Users:")
    passwords = config.get("passwords", {})
    for username in args.usernames:
        if username in passwords:
            log.info("  %s (Password remembered)", username)
        else:
            log.info("  %s (No password)", username)


def main(argv=sys.argv):
    config = load_config()
    args = parse_args(argv[1:], config)
    save_config(config)

    log_config(args, config)

    usernames = args.usernames or [raw_input("Username: "), ]
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
