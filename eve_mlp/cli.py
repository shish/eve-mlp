import os
import sys
import logging
import argparse
import subprocess
import platform
from getpass import getpass

from .login import do_login, LoginFailed
from .common import load_config, save_config, encrypt, decrypt


log = logging.getLogger(__name__)


class UserError(Exception):
    pass


def parse_args(args, config):
    parser = argparse.ArgumentParser()
    parser.add_argument("--eve-dir", help="Point to the location of the eve install folder (Remembered across runs)", default=config.get("eve-dir"), metavar="DIR")
    parser.add_argument("--singularity-dir", help="Point to the location of the singularity install folder (Remembered across runs)", default=config.get("singularity-dir"), metavar="DIR")
    parser.add_argument("--username", help="Username to log in with (Can be used multiple times, remembered across runs)", dest="usernames", action="append", default=config.get("usernames"), metavar="NAME")
    parser.add_argument("--singularity", help="Launch singularity instead of tranquility", default=False, action="store_true")
    parser.add_argument("--save-passwords", help="Save passwords for all alts (encrypted with one master password)", default=False, action="store_true")
    parser.add_argument("-d", "--dry", help="Dry-run (for MLP developers)", default=False, action="store_true")
    parser.add_argument("-v", "--verbose", help="Be more verbose (use more -v's for more verbosity)", action="count", default=0)
    parser.add_argument("-f", "--forgetful", help="Don't remember settings", default=False, action="store_true")
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


def run_mlp(args):
    config = load_config()
    args = parse_args(args, config)

    log_config(args, config)

    usernames = args.usernames or [raw_input("Username: "), ]

    master_pass = None
    if args.save_passwords:
        master_pass = getpass("Enter master password: ")

    un2pw = {}
    for username in usernames:
        if username in config.get("passwords", {}):
            if not master_pass:
                master_pass = getpass("Enter master password: ")
            password = decrypt(config["passwords"][username], master_pass)
        else:
            if len(usernames) == 1:
                password = getpass("Password: ")
            else:
                password = getpass("%s's Password: " % username)
            if args.save_passwords:
                config["passwords"][username] = encrypt(password, master_pass)
        un2pw[username] = password

    if not args.forgetful:
        save_config(config)

    for username, password in un2pw.items():
        try:
            if args.dry:
                launch_token = "not-a-real-token"
            else:
                launch_token = do_login(username, password, args)
            launch(launch_token, args)
        except LoginFailed as e:
            log.error("Login failed: %s", e)
            return 1


def launch(launch_token, args):
    log.info("Launching eve")
    cmd = []

    # platform specific pre-binary bits
    if args.dry:
        cmd.append("echo")
    if platform.system() == "Linux":
        cmd.append("wine")

    # run the app
    cmd.append("bin/ExeFile.exe")
    cmd.append("/ssoToken=" + launch_token)

    # app flags
    if args.singularity:
        cmd.append("/server:Singularity")

    # go!
    subprocess.Popen(" ".join(cmd), shell=True)


def main(argv=sys.argv):
    try:
        run_mlp(argv[1:])
    except KeyboardInterrupt:
        pass
    except UserError as e:
        print e
