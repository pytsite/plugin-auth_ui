"""PytSite Auth UI Abstract Drivers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union
from abc import ABC, abstractmethod
from pytsite import http
from plugins import form, form2

Form = Union[form.Form, form2.Form]


class Driver(ABC):
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
    def get_sign_up_form(self, request: http.Request, **kwargs) -> Form:
        """Get sign up form
        """
        pass

    @abstractmethod
    def get_sign_in_form(self, request: http.Request, **kwargs) -> Form:
        """Get sign in form
        """
        pass

    @abstractmethod
    def get_restore_account_form(self, request: http.Request, **kwargs) -> Form:
        """Get account restoration form
        """
        pass
