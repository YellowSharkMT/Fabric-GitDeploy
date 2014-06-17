from fabric.api import *
from .base import ConfigBase
from weakref import WeakKeyDictionary

class ServerInfo(WeakKeyDictionary):
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

class Server(object):
    def __init__(self, default):
        self.default = default
        self.data = ServerInfo()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        if value is not None:
            if not isinstance(value, dict):
                raise ValueError('Server must be a dictionary of values.')
            self.data[instance] = value
