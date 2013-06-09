import os
import sys
import logging
import argparse
from getpass import getpass

from eve_mlp.login import do_login, LoginFailed
from eve_mlp.common import Config, LaunchConfig, launch, LaunchFailed


log = logging.getLogger(__name__)


class UserError(Exception):
    pass


def parse_args(args, config):
    """
    This needs a lot of re-doing for the account-based config
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    list_parser = subparsers.add_parser('list', help='List all Launch Configs')
    list_parser.set_defaults(mode="list")

    launch_parser = subparsers.add_parser('launch', help='Launch a Launch Config')
    launch_parser.set_defaults(mode="launch")
    launch_parser.add_argument(
        "launches", action="append", default=[lc.confname for lc in config.launches if lc.selected], metavar="NAME", nargs="+",
        help="Launch configuration to use (can be repeated)")
    launch_parser.add_argument(
        "--save-passwords", default=config.settings["remember-passwords"], action="store_true",
        help="Save passwords for all alts (encrypted with one master password)")
    launch_parser.add_argument(
        "-d", "--dry", default=False, action="store_true",
        help="Dry-run (for MLP developers)")

    config_parser = subparsers.add_parser('config', help='Configure a Launch Config')
    config_parser.set_defaults(mode="config")
    config_parser.add_argument(
        "launch", default="(Defaults)", metavar="NAME", nargs="?",
        help="Launch configuration to use")
    config_parser.add_argument(
        "--confname", default=None, metavar="NAME",
        help="Rename the selected launch config to NAME")
    config_parser.add_argument(
        "--username", default=None, metavar="NAME",
        help="Set username for this launch config")
    config_parser.add_argument(
        "--gamepath", default=None, metavar="DIR",
        help="Point to the location of the Eve install folder")
    config_parser.add_argument(
        "--serverid", default=None,
        help="Which server to connect to (tranquility (default) or singularity)")
    config_parser.add_argument(
        "--selected", default=None,
        help="Whether or not this should be one of the default launches")

    delete_parser = subparsers.add_parser('delete', help='Delete a Launch Config')
    delete_parser.set_defaults(mode="delete")
    delete_parser.add_argument(
        "launch", metavar="NAME",
        help="Launch configuration to use")

    add_parser = subparsers.add_parser('add', help='Add a Launch Config')
    add_parser.set_defaults(mode="add")
    add_parser.add_argument(
        "launch", metavar="NAME",
        help="Launch configuration to use")

    parser.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="Be more verbose (use more -v's for more verbosity)")

    args = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)19.19s %(levelname)4.4s %(message)s")
    module_log = logging.getLogger("eve_mlp")
    module_log.setLevel(logging.WARNING - args.verbose * 10)

    # return
    return args


def get_launch_config(config, name):
    """
    Get a launch config by name
    """
    if name == "(Defaults)":
        return config.defaults

    for launch_config in config.launches:
        if launch_config.confname == name:
            return launch_config

    raise Exception("No LaunchConfig named %s" % name)


def collect_passwords(args, config):
    for name in args.launches:
        launch_config = get_launch_config(config, name)
        if launch_config.username and not launch_config.password:
            launch_config.password = getpass("Enter password for %s: " % str(launch_config.username))


def launch_all(args, config):
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


def run_mlp(args):
    config = Config()
    config.load()
    args = parse_args(args, config)

    if config.settings["remember-passwords"]:
        config.master_password = getpass("Enter Master Password: ")
        config.decrypt_passwords()

    if args.mode == "list":
        def bool2text(b):
            if b == True:
                return "Y"
            elif b == False:
                return "N"
            else:
                return "-"

        def format_launch_config(lc):
            return {
                "confname": lc._confname or "(Defaults)",
                "selected": bool2text(lc._selected),
                "serverid": lc._serverid or "-",
                "username": lc._username or "-",
                "gamepath": lc._gamepath or "-",
            }

        fmt = "%(confname)-20.20s %(selected)-9.9s %(serverid)-12.12s %(username)-10.10s %(gamepath)s"
        names = {
            "confname": "Launch Config Name",
            "selected": "Selected",
            "serverid": "Server",
            "username": "Username",
            "gamepath": "Game Path",
        }
        print fmt % names
        print "~" * 72
        print fmt % format_launch_config(config.defaults)
        for lc in config.launches:
            print fmt % format_launch_config(lc)

    if args.mode == "add":
        config.launches.append(LaunchConfig(config.defaults, {"confname": args.launch}))

    if args.mode == "config":
        def parse_val(val):
            if val == "-":
                return None
            else:
                return val

        if args.confname:
            get_launch_config(config, args.launch).confname = parse_val(args.confname)

        if args.username:
            get_launch_config(config, args.launch).username = parse_val(args.username)

        if args.gamepath:
            get_launch_config(config, args.launch).gamepath = parse_val(args.gamepath)

        if args.serverid:
            get_launch_config(config, args.launch).serverid = parse_val(args.serverid)

        #if args.selected:
        #    get_launch_config(config, args.launch).selected = args.selected

    if args.mode == "delete":
        lc = get_launch_config(config, args.launch)
        config.launches.remove(lc)

    if args.mode == "launch":
        config.settings["remember-passwords"] = args.save_passwords

        collect_passwords(args, config)
        launch_all(args, config)

    config.encrypt_passwords()
    config.save()


def main(argv=sys.argv):
    try:
        run_mlp(argv[1:])
    except KeyboardInterrupt:
        pass
    except UserError as e:
        print e
