import argparse
import logging


def parse_args(args, config):
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
    config_parser.add_argument(
        "--winecmd", default=None,
        help="Wine command (eg. 'wine explorer')")
    config_parser.add_argument(
        "--wineflags", default=None,
        help="Wine flags (eg. '/desktop=EVE,1920x1080')")

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


