"""
This file is a catch-all location for any helper functions needed by this package.
"""
# Fabric/Global Imports
from fabric.api import quiet

# Local Imports
from ..config import QUIET_COMMANDS


def filter_quiet_commands(cmd):
    """
    Takes a callable of some sort, and depending on the QUIET_COMMANDS config value, it suppresses (or doesn't) the
    output of the command. Typically this is used to suppress the output of the `local()` command from fabric.api,
    which does NOT supprt the quiet=False/True parameter.

    Example usage, showing how to wrap a `local()` command in a lambda, and feed it to this function:

    - filter_quiet_commands(lambda: local('uname -a'))
    """
    if cmd is None:
        raise ValueError('The `cmd` parameter should be a callable.')
    if QUIET_COMMANDS:
        with quiet():
            cmd()
    else:
        cmd()
