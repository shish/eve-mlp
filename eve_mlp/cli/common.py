
class UserError(Exception):
    pass


def get_launch_config(config, name):
    """
    Get a launch config by name
    """
    if name == "(Defaults)":
        return config.defaults

    for launch_config in config.launches:
        if launch_config.confname == name:
            return launch_config

    raise UserError("No LaunchConfig named %s" % name)
