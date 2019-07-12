"""PytSite Auth UI Abstract Drivers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from abc import ABC as _ABC, abstractmethod
from pytsite import http
from plugins import form


class Driver(_ABC):
    """PytSite Auth UI Abstract Driver
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get name of the driver
        """
        pass

    @property
    def name(self) -> str:
        """Get name of the driver
        """
        return self.get_name()

    @abstractmethod
    def get_description(self) -> str:
        """Get description of the driver
        """
        pass

    @property
    def description(self) -> str:
        """Get description of the driver
        """
        return self.get_description()

    @abstractmethod
    def get_sign_up_form(self, request: http.Request, **kwargs) -> form.Form:
        """Get sign up form
        """
        pass

    @abstractmethod
    def get_sign_in_form(self, request: http.Request, **kwargs) -> form.Form:
        """Get sign in form
        """
        pass

    @abstractmethod
    def get_restore_account_form(self, request: http.Request, **kwargs) -> form.Form:
        """Get account restoration form
        """
        pass
