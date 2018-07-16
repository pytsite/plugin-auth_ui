"""PytSite Auth UI Plugin Events Handlers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import router as _router, lang as _lang, mail as _mail, tpl as _tpl
from plugins import auth as _auth, hreflang as _hreflang
from . import _api


def on_router_dispatch():
    """pytsite.router.dispatch Event Handler
    """
    # Alternate languages for sign in page
    if len(_lang.langs()) > 1:
        base_path = _api.base_path()
        if base_path == _router.current_path():
            for lng in _lang.langs(False):
                _hreflang.add(lng, _router.url(base_path, lang=lng))


def on_auth_sign_up(user: _auth.AbstractUser):
    # Set session notification
    _router.session().add_success_message(_lang.t('auth_ui@registration_form_success'))

    # Send a confirmation email to the user
    if _auth.is_sign_up_confirmation_required():
        msg = _tpl.render('auth_ui@mail/{}/sign-up'.format(_lang.get_current()), {
            'user': user,
            'confirm_url': _router.rule_url('auth_ui@sign_up_confirm',
                                            {'code': user.confirmation_hash}) if not user.is_confirmed else None
        })
        _mail.Message(user.login, _lang.t('auth_ui@confirm_registration'), msg).send()

    # Send a notification emails to admins
    if _auth.is_sign_up_admins_notification_enabled():
        for admin in _auth.get_admin_users():
            msg = _tpl.render('auth_ui@mail/{}/sign-up-admin-notify'.format(_lang.get_current()), {
                'admin': admin,
                'user': user,
            })
            _mail.Message(admin.login, _lang.t('auth_ui@registration_admin_notify'), msg).send()


def on_auth_user_status_change(user: _auth.AbstractUser, status: str):
    if _auth.is_user_status_change_notification_enabled():
        msg = _tpl.render('auth_ui@mail/{}/user-status-change'.format(_lang.get_current()), {
            'user': user,
            'status': status,
        })
        _mail.Message(user.login, _lang.t('auth_ui@user_status_change_notify'), msg).send()
