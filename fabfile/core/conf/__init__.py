from fabric.api import *
import imp
import os

from .base import ConfigBase
from .commands import Commands
from .header import Header, display_header
from .server import Server

# Restrict what can be imported form this module to just these items:
__all__ = ['load_config', 'display_header']

def load_config():
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
    header = Header()

    def __init__(self, config):
        self.project_name = config.PROJECT_NAME
        self.wp_prefix = config.WP_PREFIX
        self.unversioned_folders = config.UNVERSIONED_FOLDERS
        self.post_deploy_commands = config.POST_DEPLOY_COMMANDS
        self.app_restart_commands = config.APP_RESTART_COMMANDS
        self.database_migration_commands = config.DATABASE_MIGRATION_COMMANDS
        self.show_header = config.SHOW_HEADER
        self.quiet_commands = config.QUIET_COMMANDS
        self.header = config.HEADER
        self.local = config.LOCAL
        self.dev = config.DEV
        self.prod = config.PROD

    def __unicode__(self):
        return self.project_name

