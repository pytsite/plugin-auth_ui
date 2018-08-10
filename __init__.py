"""PytSite Auth UI Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from ._controllers import AuthFilter
from . import _widget as widget, _frm as form
from ._api import base_path, register_driver, get_driver, get_drivers, sign_in_form, sign_in_url, sign_up_form, \
    sign_up_url, sign_out_url, restore_account_form
from ._driver import Driver


def plugin_load():
    from plugins import assetman

    assetman.register_package(__name__)
    assetman.t_less(__name__)
    assetman.t_js(__name__)


def plugin_install():
    from plugins import assetman

    assetman.build(__name__)


def plugin_load_uwsgi():
    from pytsite import router, lang, tpl
    from plugins import robots_txt, auth
    from . import _controllers, _eh

    # Resource packages
    lang.register_package(__name__)
    tpl.register_package(__name__)

    # Routes
    bp = base_path()
    router.handle(_controllers.Form, bp + '/sign-in', 'auth_ui@sign_in_default')
    router.handle(_controllers.Form, bp + '/sign-in/<driver>', 'auth_ui@sign_in')
    router.handle(_controllers.Form, bp + '/sign-up', 'auth_ui@sign_up_default')
    router.handle(_controllers.Form, bp + '/sign-up/<driver>', 'auth_ui@sign_up')
    router.handle(_controllers.Form, bp + '/restore/<driver>', 'auth_ui@restore_account')
    router.handle(_controllers.SignUpConfirm, bp + '/sign-up/confirm/<code>', 'auth_ui@sign_up_confirm')
    router.handle(_controllers.SignOut, bp + '/sign-out', 'auth_ui@sign_out')
    router.handle(_controllers.UserProfileView, bp + '/user/<nickname>', 'auth_ui@user_profile_view')
    router.handle(_controllers.UserProfileModify, bp + '/user/<nickname>/edit', 'auth_ui@user_profile_modify')

    # Router events
    router.on_dispatch(_eh.on_router_dispatch)

    # Auth events
    auth.on_sign_up(_eh.on_auth_sign_up)
    auth.on_user_status_change(_eh.on_auth_user_status_change)

    # robots.txt rules
    robots_txt.disallow(bp + '/')
