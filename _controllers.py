"""PytSite Auth UI Plugin Controllers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union as _Union, Optional as _Optional
from pytsite import lang as _lang, http as _http, metatag as _metatag, tpl as _tpl, router as _router, \
    logger as _logger, routing as _routing, util as _util, mail as _mail
from plugins import assetman as _assetman, auth as _auth, query as _query
from . import _api


class AuthFilterController(_routing.Controller):
    """Authorization Filter
    """

    def exec(self) -> _Optional[_http.response.Redirect]:
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
    def exec(self) -> _Union[str, _http.response.Redirect]:
        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(_router.request().inp.get('__redirect', _router.base_url()))

        rule_name = self.arg('_pytsite_router_rule_name')

        if 'sign_up' in rule_name and not _auth.is_sign_up_enabled():
            raise self.not_found()

        try:
            form_type = 'sign-in' if 'sign_in' in rule_name else 'sign-up'
            driver_name = self.arg('driver', _api.get_driver().name)
            frm = _api.sign_in_form(driver_name) if form_type == 'sign-in' else _api.sign_up_form(driver_name)

            _metatag.t_set('title', frm.title)

            tpl_args = {
                'driver': driver_name,
                'form_type': form_type,
                'form': frm,
            }

            # Try to render tpl provided by application
            try:
                return _tpl.render('auth_ui/{}'.format(form_type), tpl_args)

            # Render plugin's built-in tpl
            except _tpl.error.TemplateNotFound:
                _assetman.preload('auth_ui@css/form.css')
                return _tpl.render('auth_ui@form', tpl_args)

        except _auth.error.DriverNotRegistered:
            raise self.not_found()


class SignInSubmit(_routing.Controller):
    """Sign In Form Submit
    """

    def exec(self):
        redirect = _router.request().inp.pop('__redirect', _router.base_url())

        if isinstance(redirect, list):
            redirect = redirect.pop()

        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(redirect)

        driver_name = self.arg('driver')

        try:
            _auth.sign_in(driver_name, _router.request().inp)

        except _auth.error.UserNotActive as e:
            _logger.warn(e)
            _router.session().add_warning_message(str(e))

            redirect = self.redirect(_router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver_name,
                '__redirect': redirect,
                'login': _router.request().inp.get('login'),
            }))

        except Exception as e:
            _logger.error(e)
            _router.session().add_error_message(_lang.t('auth_ui@authentication_error'))

            redirect = self.redirect(_router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver_name,
                '__redirect': redirect,
                'login': _router.request().inp.get('login'),
            }))

        return self.redirect(redirect)


class SignUpSubmit(_routing.Controller):
    """Sign Up Form Submit
    """

    def exec(self):
        # Default redirect
        redirect = _router.request().inp.pop('__redirect', _router.base_url())

        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(redirect)

        driver_name = self.arg('driver')

        try:
            # Register a new user
            user = _auth.sign_up(driver_name, _router.request().inp)

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
                    _mail.Message(user.login, _lang.t('auth_ui@registration_admin_notify'), msg).send()

            _router.session().add_success_message(_lang.t('auth_ui@registration_form_success'))

            return self.redirect(redirect)

        except Exception as e:
            _logger.error(e)
            _router.session().add_error_message(_lang.t('auth_ui@registration_error'))

            return self.redirect(_router.rule_url('auth_ui@sign_up', rule_args={
                'driver': driver_name,
                '__redirect': redirect,
            }))


class SignUpConfirm(_routing.Controller):
    """Confirm Sign Up
    """

    def exec(self):
        try:
            user = next(_auth.find_users(_query.Query(_query.Eq('confirmation_hash', self.arg('code')))))
        except StopIteration:
            raise self.not_found()

        _auth.switch_user_to_system()
        user.confirmation_hash = None
        if user.status == 'waiting':
            user.status = _auth.get_new_user_status()
        user.save()
        _auth.restore_user()

        _router.session().add_success_message(_lang.t('auth_ui@registration_confirm_success'))

        return self.redirect(self.arg('__redirect', _api.sign_in_url()))


class SignOut(_routing.Controller):
    """Sign Out
    """

    def exec(self):
        _auth.sign_out(_auth.get_current_user())

        return self.redirect(_router.request().inp.get('__redirect', _router.base_url()))
