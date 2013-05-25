import os
import sys
import logging
import argparse
from getpass import getpass

from eve_mlp.login import do_login, LoginFailed
from eve_mlp.common import Config, launch, LaunchFailed


log = logging.getLogger(__name__)


class UserError(Exception):
    pass


def parse_args(args, config):
    """
    This needs a lot of re-doing for the account-based config
    """
    parser = argparse.ArgumentParser()

    # Specific LaunchConfig options
    parser.add_argument(  # TODO: default: look through config.launches for LaunchConfigs with the 'selected' flag set
        "--launch", dest="launches", action="append", default=[], metavar="NAME",
        help="Launch configuration to use (can be repeated)")

    # Base LaunchConfig options
    parser.add_argument(
        "--game-path", default=config.defaults.gamepath, metavar="DIR",
        help="Point to the location of the Eve install folder")
    parser.add_argument(
        "--server", default="tranquility",
        help="Which server to connect to (tranquility (default) or singularity)")

    # App options
    parser.add_argument(
        "--save-passwords", default=config.settings["remember-passwords"], action="store_true",
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
    if args.game_path:
        config.defaults.gamepath = args.game_path

    if args.server:
        config.defaults.serverid = args.server

    config.settings["remember-passwords"] = args.save_passwords

    # return
    return args


def log_config(args, config):
    log.info("MLP Software:")
    log.info("  Verbosity       : %s", args.verbose)
    log.info("")


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


def get_launch_config(config, name):
    """
    Get a launch config by name
    """
    for launch_config in config.launches:
        if launch_config.confname == name:
            return launch_config
    raise Exception("No LaunchConfig named %s" % name)


def run_mlp(args):
    config = Config()
    config.load()
    args = parse_args(args, config)
    log_config(args, config)

    if config.settings["remember-passwords"]:
        config.master_password = getpass("Enter Master Password: ")
        config.decrypt_passwords()

    logins = get_logins(args, config)

    for name in args.launches:
        try:
            launch_config = get_launch_config(config, name)
            token = None
            if launch_config.username and launch_config.password:
                token = do_login(launch_config.username, launch_config.password)
            launch(config, launch_config, token)
        except LoginFailed as e:
            log.error("Login failed: %s", e)
            return 1
        except LaunchFailed as e:
            log.error("Launch failed: %s", e)
            return 1

    if not args.forgetful:
        config.encrypt_passwords()
        config.save()


def main(argv=sys.argv):
    try:
        run_mlp(argv[1:])
    except KeyboardInterrupt:
        pass
    except UserError as e:
        print e
