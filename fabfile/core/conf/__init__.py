from fabric.api import *
import imp
import os


def config_loader():
    """
    Loads the configuration, either from the `FAB_CONFIG` environment variable, or from a
    local `fabfile/config.py` file.
    :return:
    """
    if os.environ.get('FAB_CONFIG') is not None:
        import imp

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


class ConfigBase(object):
    def get(self, prop):
        try:
            return getattr(self, prop)
        except Exception as e:
            e.message = 'Unable to access that property. ' + e.message

    def set(self, prop, value):
        try:
            return setattr(self, prop, value)
        except Exception as e:
            e.message = 'Unable to set that property/value. ' + e.message


class Server(ConfigBase):
    name = None
    hostname = 'user@server'
    hosts = ['user@server1', 'user@server2']
    home_url = 'http://subdomain.website.com/'
    wp_url = 'http://subdomain.website.com/'
    archive = '~/webapps/PROJECT_NAME/archives'
    root = '~/webapps/PROJECT_NAME/dev'
    repo = '~/webapps/PROJECT_NAME/PROJECT_NAME.git'
    db = {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    }

    def __init__(self, name, server=None):
        if name is None:
            raise ValueError('Server name must be provided.')
        self.name = name
        self.set_server(server)


    def set_server(self, server):
        if server is not None:
            if server is not dict:
                raise ValueError('Server must be a dictionary of values.')

            for key in server:
                self.set(key, server[key])


class Header(ConfigBase):
    content = []

    def __init__(self, content=None):
        if content is not None:
            self.content = content


class Commands(ConfigBase):
    commands = []

    def __init__(self, commands=None):
        if commands is not None:
            self.commands = commands


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

