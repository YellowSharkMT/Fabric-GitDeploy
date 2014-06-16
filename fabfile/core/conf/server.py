from fabric.api import *
from .base import ConfigBase

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
