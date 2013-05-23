import os
import sys
import logging
import argparse
from getpass import getpass

from .login import do_login, LoginFailed


log = logging.getLogger(__name__)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--evedir", help="Point to the location of the eve install folder")
    parser.add_argument('-v', '--verbose', action="count", default=0)
    args = parser.parse_args(args)

    logging.basicConfig(level=logging.WARNING)
    l2log = logging.getLogger("launcher2")
    l2log.setLevel(logging.WARNING - args.verbose * 10)

    if args.evedir:
        os.chdir(args.evedir)

    if not os.path.exists("bin/ExeFile.exe"):
        logging.error("Need to be run from the eve install dir, or use --evedir")
        return 1

    return args


def main(argv=sys.argv):
    args = parse_args(argv[1:])

    username = raw_input("Username: ")
    password = getpass("Password: ")

    try:
        launch_token = do_login(username, password, args)
        log.info("Launching eve")
        os.system("wine bin/ExeFile.exe /ssoToken=" + launch_token)
        return 0
    except LoginFailed as e:
        log.error("Login failed: %s", e)
        return 1
