"""PytSite Auth UI Plugin Controllers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union as _Union, Optional as _Optional
from werkzeug.utils import escape as _escape
from pytsite import lang as _lang, http as _http, metatag as _metatag, tpl as _tpl, router as _router, \
    logger as _logger, routing as _routing
from plugins import assetman as _assetman, auth as _auth
from . import _api, _widget


class AuthFilterController(_routing.Controller):
    """Authorization Filter
    """

    def exec(self) -> _Optional[_http.response.Redirect]:
        if not _auth.get_current_user().is_anonymous:
            return

        # Redirecting to the authorization endpoint
        inp = self.request.inp.copy()
        inp['__redirect'] = _escape(_router.current_url(True))
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
            frm = _api.sign_in_form(driver, nocache=True)
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
            _logger.error(str(e), exc_info=e)
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


class ProfileView(_routing.Controller):
    """Profile View Page
    """

    def exec(self) -> str:
        try:
            profile_owner = _auth.get_user(nickname=self.arg('nickname'))
        except _auth.error.UserNotFound:
            raise self.not_found()

        c_user = _auth.get_current_user()

        if _tpl.tpl_exists('auth_ui/profile-view'):
            tpl_name = 'auth_ui/profile-view'
        else:
            tpl_name = 'auth_ui@profile-view'

        # Non-public profiles cannot be viewed
        if not profile_owner.profile_is_public and c_user.login != profile_owner.login and not c_user.is_admin:
            raise self.not_found()

        # Page title
        _metatag.t_set('title', profile_owner.full_name)

        # Widgets
        profile_widget = _widget.Profile('auth-ui-profile-widget', user=profile_owner)

        self.args.update({
            'profile_is_editable': c_user == profile_owner or c_user.is_admin,
            'user': profile_owner,
            'profile_widget': profile_widget,
        })

        # Give control of the response to an alternate endpoint
        if _router.has_rule('auth_ui_profile_view'):
            self.args.update({
                'tpl': tpl_name,
            })

            return _router.call('auth_ui_profile_view', self.args)

        # Default response
        return _tpl.render(tpl_name, self.args)


class ProfileEdit(_routing.Controller):
    """User Profile Edit
    """

    def exec(self) -> str:
        raise NotImplementedError()

        # TODO: Following code is obsolete and needs rewriting
        #
        # # Check if the profile owner is exists
        # profile_owner = _auth.get_user(nickname=self.arg('nickname'))
        # if not profile_owner:
        #     raise self.not_found()
        #
        # tpl_name = 'auth_ui@profile-edit'
        #
        # frm = _api.user_modify_form(profile_owner)
        # frm.title = _lang.t('auth_ui@profile_edit')
        # frm.redirect = profile_owner.profile_view_url
        #
        # _metatag.t_set('title', frm.title)
        #
        # # Give control of the response to an alternate endpoint
        # if _router.has_rule('$theme@auth_ui_profile_edit'):
        #     self.args.update({
        #         'tpl': tpl_name,
        #         'user': profile_owner,
        #         'frm': frm,
        #     })
        #     return _router.call('$theme@auth_ui_profile_edit', self.args)
        #
        # # Default response
        # return _tpl.render(tpl_name, {'frm': frm})
