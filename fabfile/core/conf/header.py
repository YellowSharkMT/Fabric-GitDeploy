from fabric.api import *
from .base import ConfigBase

class Header(ConfigBase):
    content = []

    def __init__(self, content=None):
        if content is not None:
            self.content = content

