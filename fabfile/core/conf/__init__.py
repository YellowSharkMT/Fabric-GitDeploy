from fabric.api import *
import imp
import os

from .base import ConfigBase
from .commands import Commands
from .header import Header
from .server import Server

def config_loader():
    """
    Loads the configuration, either from the `FAB_CONFIG` environment variable, or from a
    local `fabfile/config.py` file.
    :return:
    """
    if os.environ.get('FAB_CONFIG') is not None:
        try:
            config = imp.load_source('config', os.environ.get('FAB_CONFIG'))
        except ImportError as e:
            raise ImportError('Unable to load configuration from the ENV variable. ' + e.message)
    else:
        try:
            from fabfile import config
        except ImportError as e:
            raise ImportError('Unable to load config, no fabfile/config.py file was found. ' + e.message)

    try:
        env.conf = Config(config)
    except ImportError as e:
        raise Exception('There was a problem loading the configuration values: ' + e.message)


class Config(ConfigBase):
    """
    Main Configuration object for the Fabric-GitDeploy package, gets attached to the Fabric `env`
    variable as `env.conf`
    """

    project_name = None
    show_header = False
    unversioned_folders = []
    wp_prefix = 'wp'
    quiet_commands = False
    local = Server('local')
    dev = Server('dev')
    prod = Server('prod')
    post_deploy_commands = Commands()
    app_restart_commands = Commands()
    database_migration_commands = Commands()
    fabfile_header = Header()

    def __init__(self, config):
        try:
            foo = config.LOCAL
        except Exception as e:
            e.message = 'Could not access the LOCA variable. ' + e.message
            raise e

        pass

