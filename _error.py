"""PytSite Auth UI Plugin Errors
"""

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Error(Exception):
    pass


class NoDriversRegistered(Error):
    def __str__(self) -> str:
        return "There is no authentication UI drivers registered"


class DriverNotRegistered(Error):
    def __init__(self, name: str):
        self._name = name

    def __str__(self) -> str:
        return "Authentication UI driver '{}' not registered".format(self._name)


class DriverAlreadyRegistered(Error):
    def __init__(self, name: str):
        self._name = name

    def __str__(self) -> str:
        return "Authentication UI driver '{}' is already registered".format(self._name)
