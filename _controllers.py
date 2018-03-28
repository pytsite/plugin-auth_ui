"""PytSite Auth UI Plugin Controllers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union as _Union, Optional as _Optional
from pytsite import lang as _lang, http as _http, metatag as _metatag, tpl as _tpl, router as _router, \
    logger as _logger, routing as _routing, util as _util
from plugins import assetman as _assetman, auth as _auth
from . import _api


class AuthFilterController(_routing.Controller):
    """Authorization Filter
    """

    def exec(self) -> _Optional[_http.response.Redirect]:
        if not _auth.get_current_user().is_anonymous:
            return

        # Redirecting to the authorization endpoint
        inp = self.request.inp.copy()
        inp['__redirect'] = _util.escape_html(_router.current_url(True))
        inp['driver'] = _api.get_driver().name

        if '__form_location' in inp:
            del inp['__form_location']

        return self.redirect(_router.rule_url('auth_ui@sign_in', inp))


class SignIn(_routing.Controller):
    """Sign In Page
    """

    def exec(self) -> _Union[str, _http.response.Redirect]:
        # Redirect user if it already authenticated
        if not _auth.get_current_user().is_anonymous:
            return self.redirect(_router.request().inp.get('__redirect', _router.base_url()))

        _assetman.preload('auth_ui@css/sign-in.css')
        _metatag.t_set('title', _lang.t('auth_ui@authentication'))

        try:
            driver = self.arg('driver')
            frm = _api.sign_in_form(driver)
            args = {'driver': driver, 'form': frm}

            try:
                return _tpl.render('auth_ui/sign-in', args)
            except _tpl.error.TemplateNotFound:
                return _tpl.render('auth_ui@sign-in', args)

        except _auth.error.DriverNotRegistered:
            raise self.not_found()


class SignInSubmit(_routing.Controller):
    """Sign In Page Submit
    """

    def exec(self):
        inp = _router.request().inp

        for i in ('__form_steps', '__form_step'):
            if i in inp:
                del inp[i]

        driver = self.arg('driver')

        redirect = inp.pop('__redirect', _router.base_url())
        if isinstance(redirect, list):
            redirect = redirect.pop()

        try:
            _auth.sign_in(driver, inp)
            return self.redirect(redirect)

        except (_auth.error.AuthenticationError, _auth.error.UserNotFound):
            _router.session().add_error_message(_lang.t('auth_ui@authentication_error'))

            return self.redirect(_router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver,
                '__redirect': redirect,
            }))

        except Exception as e:
            _logger.error(e)
            _router.session().add_error_message(str(e))
            return self.redirect(_router.rule_url('auth_ui@sign_in', rule_args={
                'driver': driver,
                '__redirect': redirect,
            }))


class SignOut(_routing.Controller):
    """Sign Out
    """

    def exec(self):
        _auth.sign_out(_auth.get_current_user())

        return self.redirect(_router.request().inp.get('__redirect', _router.base_url()))
