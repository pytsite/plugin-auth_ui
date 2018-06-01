"""PytSite Auth UI Plugin Events Handlers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from datetime import datetime as _datetime
from pytsite import router as _router, lang as _lang, http as _http, mail as _mail, tpl as _tpl
from plugins import auth as _auth, hreflang as _hreflang
from . import _api


def router_dispatch():
    """pytsite.router.dispatch Event Handler
    """
    # User is anonymous by default
    user = _auth.get_anonymous_user()

    # Determine current user based on session's data
    if 'auth.login' in _router.session():
        try:
            session = _router.session()
            user = _auth.get_user(session['auth.login'])
            session.modified = True  # Update session's timestamp
        except _auth.error.UserNotFound:
            # User has been deleted, so delete session information about it
            del _router.session()['auth.login']

    # Set current user
    _auth.switch_user(user)

    if not user.is_anonymous:
        if user.status == _auth.USER_STATUS_ACTIVE:
            # Disable page caching for signed in users
            _router.no_cache(True)

            # Update user's activity timestamp
            user.last_activity = _datetime.now()
            user.save()
        else:
            # Sign out inactive user
            _auth.sign_out(user)

    # Alternate languages for sign in page
    if len(_lang.langs()) > 1:
        base_path = _api.base_path()
        if base_path == _router.current_path():
            for lng in _lang.langs(False):
                _hreflang.add(lng, _router.url(base_path, lang=lng))


def router_response(response: _http.Response):
    # If user signed out, but session cookie is still alive
    if 'PYTSITE_SESSION' in _router.request().cookies and _auth.get_current_user().is_anonymous:
        try:
            _router.delete_session()
        except KeyError:
            pass

        response.delete_cookie('PYTSITE_SESSION')


def auth_user_status_change(user: _auth.AbstractUser, status: str):
    if _auth.is_user_status_change_notification_enabled():
        msg = _tpl.render('auth_ui@mail/{}/user-status-change'.format(_lang.get_current()), {
            'user': user,
            'status': status,
        })
        _mail.Message(user.login, _lang.t('auth_ui@user_status_change_notify'), msg).send()
