"""PytSite Auth UI Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import _widget as widget, _frm as form, _http_api_controllers as http_api_controllers
from ._controllers import AuthFilter
from ._api import base_path, register_driver, get_driver, get_drivers, sign_in_form, sign_in_url, sign_up_form, \
    sign_up_url, sign_out_url, restore_account_form, role_form, user_form
from ._driver import Driver


def plugin_load_wsgi():
    from pytsite import router
    from plugins import robots_txt, auth, http_api
    from . import _controllers, _http_api_controllers, _eh

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

    # HTTP API routes
    http_api.handle('GET', 'auth_ui/widget/user_select', _http_api_controllers.GetWidgetUserSelect,
                    'auth_ui@get_widget_user_select')

    # Events handlers
    auth.on_sign_up(_eh.on_auth_sign_up)
    auth.on_user_status_change(_eh.on_auth_user_status_change)
    auth.on_user_as_jsonable(_eh.on_auth_user_as_jsonable)

    # robots.txt rules
    robots_txt.disallow(bp + '/')
