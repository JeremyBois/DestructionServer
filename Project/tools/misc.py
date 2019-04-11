# Project/tools/host.py


__all__ = ['classproperty']


class classproperty(object):

    """Read only class property."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
