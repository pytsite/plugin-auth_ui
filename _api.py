"""PytSite Auth UI Plugin API Functions
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Dict as _Dict, Union as _Union
from collections import OrderedDict as _OrderedDict
from pytsite import router as _router, lang as _lang, reg as _reg
from plugins import form as _form
from . import _error, _frm
from ._driver import Driver as _Driver

_drivers = _OrderedDict()  # type: _Dict[str, _Driver]


def base_path() -> str:
    """Get base path of Auth UI controllers
    """
    return _reg.get('auth_ui.base_path', '/auth')


def register_driver(driver: _Driver):
    """Register a driver
    """
    if driver.name in _drivers:
        raise _error.DriverAlreadyRegistered(driver.name)

    _drivers[driver.name] = driver


def get_driver(name: str = None) -> _Driver:
    """Get a driver
    """
    if not _drivers:
        raise _error.NoDriversRegistered()

    if name:
        try:
            return _drivers[name]
        except KeyError:
            raise _error.DriverNotRegistered(name)

    else:
        d_names = list(_drivers.keys())

        try:
            # Try to get default driver defined in registry
            return _drivers[_reg.get('auth.ui_driver', d_names[0])]

        except KeyError:
            # Get first registered driver
            return _drivers[d_names[0]]


def get_drivers() -> _Dict[str, _Driver]:
    """Get registered drivers
    """
    return _drivers.copy()


def sign_in_form(driver_name: str = None, **kwargs) -> _form.Form:
    """Get a sign in form
    """
    driver = get_driver(driver_name)

    kwargs.update({
        'name': kwargs.get('name', 'auth-ui-sign-in-' + driver.name),
        'css': kwargs.get('css', '') + ' auth-ui-form auth-ui-sign-in driver-' + driver.name
    })

    form = driver.get_sign_in_form(**kwargs)
    form.action = _router.rule_url('auth_ui@sign_in_submit', {'driver': driver.name})

    if not form.title:
        form.title = _lang.t('auth_ui@authentication')

    return form


def sign_in_url(driver_name: str = None, redirect: _Union[str, bool] = False, add_query: dict = None,
                add_fragment: str = None) -> str:
    """Get sign in URL
    """
    rule_args = {
        'driver': get_driver(driver_name).name,
    }

    if redirect:
        rule_args['__redirect'] = redirect

    return _router.rule_url('auth_ui@sign_in', rule_args, query=add_query, fragment=add_fragment)


def sign_up_form(driver_name: str = None, **kwargs) -> _form.Form:
    """Get a sign up form
    """
    driver = get_driver(driver_name)

    kwargs.update({
        'name': kwargs.get('name', 'auth-ui-sign-up-' + driver.name),
        'css': kwargs.get('css', '') + ' auth-ui-form auth-ui-sign-up driver-' + driver.name
    })

    form = driver.get_sign_up_form(**kwargs)
    form.action = _router.rule_url('auth_ui@sign_up_submit', {'driver': driver.name})

    if not form.title:
        form.title = _lang.t('auth_ui@registration')

    return form


def sign_up_url(driver_name: str = None, add_query: dict = None, add_fragment: str = None) -> str:
    """Get sign up URL
    """
    return _router.rule_url('auth_ui@sign_up', {
        'driver': get_driver(driver_name).name,
        '__redirect': _router.current_url(add_query=add_query, add_fragment=add_fragment)
    })


def sign_out_url() -> str:
    """Get sign out URL
    """
    return _router.rule_url('auth_ui@sign_out', {'__redirect': _router.current_url()})
