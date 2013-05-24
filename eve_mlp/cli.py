import os
import sys
import logging
import argparse
from getpass import getpass

from .login import do_login, LoginFailed
from .common import load_config, save_config, encrypt, decrypt, launch


log = logging.getLogger(__name__)


class UserError(Exception):
    pass


def parse_args(args, config):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eve-dir", default=config.get("eve-dir"), metavar="DIR",
        help="Point to the location of the eve install folder (Remembered across runs)")
    parser.add_argument(
        "--singularity-dir", default=config.get("singularity-dir"), metavar="DIR",
        help="Point to the location of the singularity install folder (Remembered across runs)")
    parser.add_argument(
        "--username", dest="usernames", action="append", default=config.get("usernames"), metavar="NAME",
        help="Username to log in with (Can be used multiple times, remembered across runs)")
    parser.add_argument(
        "--singularity", default=False, action="store_true",
        help="Launch singularity instead of tranquility")
    parser.add_argument(
        "--save-passwords", default=False, action="store_true",
        help="Save passwords for all alts (encrypted with one master password)")
    parser.add_argument(
        "-d", "--dry", default=False, action="store_true",
        help="Dry-run (for MLP developers)")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="Be more verbose (use more -v's for more verbosity)")
    parser.add_argument(
        "-f", "--forgetful", default=False, action="store_true",
        help="Don't remember settings")
    args = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)19.19s %(levelname)4.4s %(message)s")
    module_log = logging.getLogger("eve_mlp")
    module_log.setLevel(logging.WARNING - args.verbose * 10)

    # update remembered config
    if args.eve_dir:
        config["eve-dir"] = args.eve_dir

    if args.singularity_dir:
        config["singularity-dir"] = args.singularity_dir

    if args.usernames:
        config["usernames"] = args.usernames

    # move to the configured directory
    if args.singularity:
        if config.get("singularity-dir"):
            os.chdir(config["singularity-dir"])
    else:
        if config.get("eve-dir"):
            os.chdir(config["eve-dir"])

    if not os.path.exists("bin/ExeFile.exe"):
        raise UserError("Need to be run from the eve install dir, or use --eve-dir")

    # return
    return args


def log_config(args, config):
    log.info("MLP Software:")
    log.info("  Verbosity       : %s", args.verbose)
    log.info("  Launching       : %s", "Singularity" if args.singularity else "EVE")
    log.info("")

    log.info("Eve Software:")
    log.info("  Eve dir         : %s", args.eve_dir)
    log.info("  Singularity dir : %s", args.singularity_dir)
    log.info("")

    log.info("Users:")
    passwords = config.get("passwords", {})
    for username in args.usernames:
        if username in passwords:
            log.info("  %s (Password remembered)", username)
        else:
            log.info("  %s (No password)", username)


def get_logins(args, config):
    usernames = args.usernames or [raw_input("Username: "), ]

    master_pass = None
    if args.save_passwords:
        master_pass = getpass("Enter master password: ")

    logins = {}
    for username in usernames:
        password = None

        if username in config.get("passwords", {}):
            if not master_pass:
                master_pass = getpass("Enter master password: ")
            password = decrypt(config["passwords"][username], master_pass)

        if not password:
            if len(usernames) == 1:
                password = getpass("Password: ")
            else:
                password = getpass("%s's Password: " % username)
            if args.save_passwords:
                config["passwords"][username] = encrypt(password, master_pass)

        logins[username] = password

    return logins


def run_mlp(args):
    config = load_config()
    args = parse_args(args, config)
    log_config(args, config)
    logins = get_logins(args, config)

    if not args.forgetful:
        save_config(config)

    for username, password in logins.items():
        try:
            if args.dry:
                launch_token = "not-a-real-token"
            else:
                launch_token = do_login(username, password)
            launch(launch_token, args)
        except LoginFailed as e:
            log.error("Login failed: %s", e)
            return 1


def main(argv=sys.argv):
    try:
        run_mlp(argv[1:])
    except KeyboardInterrupt:
        pass
    except UserError as e:
        print e
