"""PytSite Auth UI Plugin Controllers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union as _Union, Optional as _Optional
from pytsite import lang as _lang, http as _http, metatag as _metatag, tpl as _tpl, router as _router, mail as _mail, \
    logger as _logger, routing as _routing, util as _util
from plugins import assetman as _assetman, auth as _auth, query as _query
from . import _api, _frm


class AuthFilter(_routing.Filter):
    """Authorization Filter
    """

    def exec(self) -> _Optional[_http.RedirectResponse]:
        if not _auth.get_current_user().is_anonymous:
            return

        # Redirecting to the authorization endpoint
        inp = self.request.inp.copy()
        inp.update({
            'driver': _api.get_driver().name,
            '__redirect': _util.escape_html(_router.current_url(True)),
        })

        return self.redirect(_router.rule_url('auth_ui@sign_in', inp))


class Form(_routing.Controller):
    def exec(self) -> _Union[str, _http.RedirectResponse]:
        # Redirect to the base URL if user is authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(self.arg('__redirect', _router.base_url()))

        # Determine driver's name from argument or get default
        try:
            driver_name = self.arg('driver', _api.get_driver().name)
        except _auth.error.DriverNotRegistered:
            raise self.not_found()

        rule_name = self.arg('_pytsite_router_rule_name')
        if 'sign_in' in rule_name:
            form_type = 'sign-in'
            form = _api.sign_in_form(self.request, driver_name)

        elif 'sign_up' in rule_name:
            # Check if sign up is enabled
            if not _auth.is_sign_up_enabled():
                raise self.not_found()

            form_type = 'sign-up'
            form = _api.sign_up_form(self.request, driver_name)

        elif 'restore_account' in rule_name:
            form_type = 'restore-account'
            form = _api.restore_account_form(self.request, driver_name)
            form.redirect = _router.base_url()

        else:
            raise ValueError('Unsupported form type')

        if not form.redirect:
            form.redirect = _router.base_url()

        _metatag.t_set('title', form.title)

        tpl_args = {
            'driver': driver_name,
            'form_type': form_type,
            'form': form,
        }

        # Try to render tpl provided by application
        try:
            return _tpl.render('auth_ui/form', tpl_args)

        # Render plugin's built-in tpl
        except _tpl.error.TemplateNotFound:
            _assetman.preload('auth_ui@css/form.css')
            return _tpl.render('auth_ui@form', tpl_args)


class SignInSubmit(_routing.Controller):
    """Sign In Form Submit
    """

    def exec(self):
        redirect = self.arg('__redirect', _router.base_url())

        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(redirect)

        driver_name = self.arg('driver')

        try:
            _auth.sign_in(driver_name, self.args)

        except _auth.error.UserNotActive as e:
            _logger.warn(e)
            _router.session().add_warning_message(str(e))

            redirect = _router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver_name,
                'login': self.arg('login'),
                '__redirect': redirect,
            })

        except Exception as e:
            _logger.error(e)
            _router.session().add_error_message(_lang.t('auth_ui@authentication_error'))

            redirect = _router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver_name,
                'login': self.arg('login'),
                '__redirect': redirect,
            })

        return self.redirect(redirect)


class SignUpSubmit(_routing.Controller):
    """Sign Up Form Submit
    """

    def exec(self):
        # Default redirect
        redirect_url = self.args.pop('__redirect', _router.base_url())

        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(redirect_url)

        driver_name = self.arg('driver')

        try:
            # Register a new user
            user = _auth.sign_up(driver_name, self.args)

            # Send a confirmation email to the user
            msg = _tpl.render('auth_ui@mail/{}/sign-up'.format(_lang.get_current()), {
                'user': user,
                'confirm_url': _router.rule_url('auth_ui@sign_up_confirm',
                                                {'code': user.confirmation_hash}) if not user.is_confirmed else None
            })
            _mail.Message(user.login, _lang.t('auth_ui@confirm_registration'), msg).send()

            if _auth.is_sign_up_admins_notification_enabled():
                for admin in _auth.get_admin_users():
                    msg = _tpl.render('auth_ui@mail/{}/sign-up-admin-notify'.format(_lang.get_current()), {
                        'admin': admin,
                        'user': user,
                    })
                    _mail.Message(admin.login, _lang.t('auth_ui@registration_admin_notify'), msg).send()

            _router.session().add_success_message(_lang.t('auth_ui@registration_form_success'))

            return self.redirect(redirect_url)

        except Exception as e:
            _logger.error(e)
            _router.session().add_error_message(_lang.t('auth_ui@registration_error'))

            return self.redirect(_router.rule_url('auth_ui@sign_up', rule_args={
                'driver': driver_name,
                '__redirect': redirect_url,
            }))


class SignUpConfirm(_routing.Controller):
    """Confirm Sign Up
    """

    def exec(self):
        try:
            user = next(_auth.find_users(_query.Query(_query.Eq('confirmation_hash', self.arg('code')))))
        except StopIteration:
            return self.redirect(self.arg('__redirect', _api.sign_in_url()))

        try:
            _auth.switch_user_to_system()
            user.confirmation_hash = None
            if user.status == _auth.USER_STATUS_WAITING:
                user.status = _auth.get_new_user_status()
            user.save()
        finally:
            _auth.restore_user()

        _router.session().add_success_message(_lang.t('auth_ui@registration_confirm_success'))

        return self.redirect(self.arg('__redirect', _api.sign_in_url()))


class SignOut(_routing.Controller):
    """Sign Out
    """

    def exec(self):
        _auth.sign_out(_auth.get_current_user())

        return self.redirect(self.arg('__redirect', _router.base_url()))


class UserProfileView(_routing.Controller):
    """User Profile View
    """

    def __init__(self):
        super().__init__()

        self.args.add_validation('nickname', _auth.user_nickname_rule)

    def exec(self) -> str:
        try:
            user = _auth.get_user(nickname=self.arg('nickname'))
        except _auth.error.UserNotFound:
            raise self.not_found()

        if not user.is_active:
            raise self.not_found()

        c_user = _auth.get_current_user()
        if not user.is_public and not (c_user == user or c_user.is_admin):
            raise self.not_found()

        self.args['user'] = user
        _metatag.t_set('title', _lang.t('auth_ui@profile_view_title', {'name': user.full_name}))

        try:
            return _router.call('auth_ui_user_profile_view', self.args)
        except _routing.error.RuleNotFound:
            return _tpl.render('auth_ui/user_profile_view', self.args)


class UserProfileModify(_routing.Controller):
    """User Profile Edit Form
    """

    def __init__(self):
        super().__init__()

        self.args.add_validation('nickname', _auth.user_nickname_rule)

    def exec(self) -> str:
        try:
            self.args['form'] = _frm.User(self.request, user_uid=_auth.get_user(nickname=self.arg('nickname')).uid)
        except _auth.error.UserNotFound:
            raise self.not_found()

        _metatag.t_set('title', _lang.t('auth_ui@profile_edit_title'))

        try:
            return _router.call('auth_ui_user_profile_modify', self.args)
        except _routing.error.RuleNotFound:
            return _tpl.render('auth_ui/user_profile_modify', self.args)
