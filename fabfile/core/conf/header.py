from fabric.api import *
from .base import ConfigBase

def display_header():
    if env.conf.show_header and len(env.conf.header) > 0:
        for line in env.conf.header:
            print(line)

class Header(object):
    def __init__(self, content=None):
        self.content = content

    def __get__(self, instance, owner):
        return self.content

    def __set__(self, instance, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError('Header must be a list of lines to display.')
            self.content = value