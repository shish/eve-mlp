import os
import sys
import logging
from getpass import getpass

from eve_mlp.login import do_login, LoginFailed
from eve_mlp.common import Config, LaunchConfig, launch, LaunchFailed
from eve_mlp.cli.common import UserError, get_launch_config
from eve_mlp.cli.args import parse_args


log = logging.getLogger(__name__)


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

        if args.winecmd:
            get_launch_config(config, args.launch).winecmd = parse_val(args.winecmd)

        if args.wineflags:
            get_launch_config(config, args.launch).wineflags = parse_val(args.wineflags)

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
