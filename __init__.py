"""PytSite Auth UI Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from ._controllers import AuthFilterController
from ._api import base_path, register_driver, get_driver, get_drivers, sign_in_form, sign_in_url, sign_out_url, \
    user_profile_view_url, user_profile_edit_url
from . import _widget as widget
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
    from plugins import robots_txt
    from . import _controllers, _eh

    # Localization resources
    lang.register_package(__name__)

    # Routes
    bp = base_path()
    router.handle(_controllers.SignIn, bp + '/sign-in/<driver>', 'auth_ui@sign_in')
    router.handle(_controllers.SignInSubmit, bp + '/sign-in/<driver>/post', 'auth_ui@sign_in_submit', methods='POST')
    router.handle(_controllers.SignOut, bp + '/sign-out', 'auth_ui@sign_out')
    router.handle(_controllers.ProfileView, bp + '/user/<nickname>', 'auth_ui@user_profile_view')
    router.handle(_controllers.ProfileEdit, bp + '/user/<nickname>/edit', 'auth_ui@user_profile_edit',
                  filters=AuthFilterController)

    # Router events
    router.on_dispatch(_eh.router_dispatch, -999, '*')
    router.on_xhr_dispatch(_eh.router_dispatch, -999, '*')
    router.on_response(_eh.router_response, -999, '*')
    router.on_xhr_response(_eh.router_response, -999, '*')

    # Template engine globals
    tpl.register_package(__name__, alias='auth_ui')

    # robots.txt rules
    robots_txt.disallow(bp + '/')
