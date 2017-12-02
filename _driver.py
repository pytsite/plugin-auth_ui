"""PytSite Auth UI Abstract Drivers
"""
from abc import ABC as _ABC, abstractmethod as _abstractmethod
from plugins import form as _form

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Driver(_ABC):
    """PytSite Auth UI Abstract Driver
    """

    @_abstractmethod
    def get_name(self) -> str:
        """Get name of the driver
        """
        pass

    @property
    def name(self) -> str:
        """Get name of the driver
        """
        return self.get_name()

    @_abstractmethod
    def get_description(self) -> str:
        """Get description of the driver
        """
        pass

    @property
    def description(self) -> str:
        """Get description of the driver
        """
        return self.get_description()

    @_abstractmethod
    def get_sign_up_form(self, **kwargs) -> _form.Form:
        """Get sign up form
        """
        pass

    @_abstractmethod
    def get_sign_in_form(self, **kwargs) -> _form.Form:
        """Get sign in form
        """
        pass
