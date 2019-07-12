"""PytSite Auth UI Plugin API Functions
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Dict
from collections import OrderedDict
from pytsite import router, lang, reg, http, util
from plugins import form, http_api
from . import _error
from ._driver import Driver as _Driver

_drivers = OrderedDict()  # type: Dict[str, _Driver]


def base_path() -> str:
    """Get base path of Auth UI controllers
    """
    return reg.get('auth_ui.base_path', '/auth')


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
            return _drivers[reg.get('auth.ui_driver', d_names[0])]

        except KeyError:
            # Get first registered driver
            return _drivers[d_names[0]]


def get_drivers() -> Dict[str, _Driver]:
    """Get registered drivers
    """
    return _drivers.copy()


def sign_in_form(request: http.Request = None, driver_name: str = None, **kwargs) -> form.Form:
    """Get a sign in form
    """
    driver = get_driver(driver_name)

    kwargs.update({
        'name': kwargs.get('name', 'auth-ui-sign-in-' + driver.name),
        'css': kwargs.get('css', '') + ' auth-ui-form auth-ui-sign-in driver-' + driver.name
    })

    frm = driver.get_sign_in_form(request or router.request(), **kwargs)
    frm.action = http_api.url('auth_http_api@post_sign_in', {'driver': driver.name})

    if not frm.title:
        frm.title = lang.t('auth_ui@authentication')

    return frm


def sign_in_url(driver_name: str = None, redirect: str = 'CURRENT_URL', add_query: dict = None,
                add_fragment: str = '') -> str:
    """Get sign in URL
    """
    rule_args = {
        'driver': get_driver(driver_name).name,
    }

    if redirect:
        rule_args['__redirect'] = redirect.replace('CURRENT_URL', router.current_url())

    return router.rule_url('auth_ui@sign_in', rule_args, query=add_query, fragment=add_fragment)


def sign_up_form(request: http.Request = None, driver_name: str = None, **kwargs) -> form.Form:
    """Get a sign up form
    """
    driver = get_driver(driver_name)

    kwargs.update({
        'name': kwargs.get('name', 'auth-ui-sign-up-' + driver.name),
        'css': kwargs.get('css', '') + ' auth-ui-form auth-ui-sign-up driver-' + driver.name
    })

    frm = driver.get_sign_up_form(request or router.request(), **kwargs)
    frm.action = http_api.url('auth_http_api@post_sign_up', {'driver': driver.name})

    if not frm.title:
        frm.title = lang.t('auth_ui@registration')

    return frm


def sign_up_url(driver_name: str = None, add_query: dict = None, add_fragment: str = '') -> str:
    """Get sign up URL
    """
    return router.rule_url('auth_ui@sign_up', {
        'driver': get_driver(driver_name).name,
        '__redirect': router.current_url(query=add_query, fragment=add_fragment)
    })


def sign_out_url(redirect: str = 'CURRENT_URL') -> str:
    """Get sign out URL
    """
    rule_args = {'__redirect': redirect.replace('CURRENT_URL', router.current_url())} if redirect else {}

    return router.rule_url('auth_ui@sign_out', rule_args)


def restore_account_form(request: http.Request = None, driver_name: str = None, **kwargs) -> form.Form:
    """Get account restoration form
    """
    driver = get_driver(driver_name)

    kwargs.update({
        'name': kwargs.get('name', 'auth-ui-restore-account-' + driver.name),
        'css': kwargs.get('css', '') + ' auth-ui-form auth-ui-restore-account driver-' + driver.name
    })

    frm = driver.get_restore_account_form(request or router.request(), **kwargs)

    if not frm.title:
        frm.title = lang.t('auth_ui@restore_account')

    return frm


def role_form(request: http.Request = None, role_uid: str = None) -> form.Form:
    """Get role edit form
    """
    form_cls = util.get_module_attr(reg.get('auth_ui.role_form_class', 'plugins.auth_ui._frm.Role'))

    return form_cls(request or router.request(), role_uid=role_uid)


def user_form(request: http.Request = None, user_uid: str = None) -> form.Form:
    """Get user edit form
    """
    form_cls = util.get_module_attr(reg.get('auth_ui.user_form_class', 'plugins.auth_ui._frm.User'))

    return form_cls(request or router.request(), user_uid=user_uid)
