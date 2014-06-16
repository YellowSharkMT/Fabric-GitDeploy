from fabric.api import *
from .base import ConfigBase


class Commands(ConfigBase):
    commands = []

    def __init__(self, commands=None):
        if commands is not None:
            self.commands = commands


