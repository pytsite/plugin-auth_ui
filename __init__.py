"""PytSite Auth UI Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import plugman as _plugman

if _plugman.is_installed(__name__):
    # Public API
    from ._controllers import AuthFilterController
    from ._api import base_path, register_driver, get_driver, get_drivers, sign_in_form, sign_in_url, sign_out_url
    from . import _widget as widget
    from ._driver import Driver


def _register_assetman_resources():
    from plugins import assetman

    if not assetman.is_package_registered(__name__):
        assetman.register_package(__name__)
        assetman.t_less(__name__)
        assetman.t_js(__name__)
        assetman.js_module('auth-ui-widget-follow', __name__ + '@js/widget-follow')
        assetman.js_module('auth-ui-widget-profile', __name__ + '@js/widget-profile')

    return assetman


def plugin_install():
    _register_assetman_resources().build(__name__)


def plugin_load():
    _register_assetman_resources()


def plugin_load_uwsgi():
    from pytsite import router, lang, tpl
    from plugins import auth, robots_txt
    from . import _controllers, _eh

    # Localization resources
    lang.register_package(__name__)

    # Routes
    bp = base_path()
    router.handle(_controllers.SignIn, bp + '/sign-in/<driver>', 'auth_ui@sign_in')
    router.handle(_controllers.SignInSubmit, bp + '/sign-in/<driver>/post', 'auth_ui@sign_in_submit', methods='POST')
    router.handle(_controllers.SignOut, bp + '/sign-out', 'auth_ui@sign_out')
    router.handle(_controllers.ProfileView, bp + '/profile/<nickname>', 'auth_ui@profile_view')
    router.handle(_controllers.ProfileEdit, bp + '/profile/<nickname>/edit', 'auth_ui@profile_edit',
                  filters=AuthFilterController)

    # Router events
    router.on_dispatch(_eh.router_dispatch, -999, '*')
    router.on_xhr_dispatch(_eh.router_dispatch, -999, '*')
    router.on_response(_eh.router_response, -999, '*')
    router.on_xhr_response(_eh.router_response, -999, '*')

    # Template engine globals
    tpl.register_package(__name__, alias='auth_ui')
    tpl.register_global('auth_current_user', auth.get_current_user)
    tpl.register_global('auth_sign_in_url', sign_in_url)
    tpl.register_global('auth_sign_out_url', sign_out_url)

    # robots.txt rules
    robots_txt.disallow(bp + '/')
