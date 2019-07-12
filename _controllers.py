"""PytSite Auth UI Plugin Controllers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union, Optional
from pytsite import lang, http, metatag, tpl, router, util, routing
from plugins import auth, query
from . import _api


class AuthFilter(routing.Filter):
    """Authorization Filter
    """

    def before(self) -> Optional[http.RedirectResponse]:
        if not auth.get_current_user().is_anonymous:
            return

        # Redirecting to the authorization endpoint
        inp = self.request.inp.copy()
        inp.update({
            'driver': _api.get_driver().name,
            '__redirect': util.escape_html(router.current_url(True)),
        })

        return self.redirect(router.rule_url('auth_ui@sign_in', inp))


class Form(routing.Controller):
    def exec(self) -> Union[str, http.RedirectResponse]:
        # Redirect to the base URL if user is already authenticated
        if not auth.get_current_user().is_anonymous:
            return self.redirect(self.arg('__redirect', router.base_url()))

        # Determine driver's name from argument or get default
        try:
            driver_name = self.arg('driver', _api.get_driver().name)
        except auth.error.DriverNotRegistered:
            raise self.not_found()

        rule_name = self.arg('_pytsite_router_rule_name')
        if 'sign_in' in rule_name:
            form_type = 'sign-in'
            form = _api.sign_in_form(self.request, driver_name)

        elif 'sign_up' in rule_name:
            # Check if sign up is enabled
            if not auth.is_sign_up_enabled():
                raise self.not_found()

            form_type = 'sign-up'
            form = _api.sign_up_form(self.request, driver_name)

        elif 'restore_account' in rule_name:
            form_type = 'restore-account'
            form = _api.restore_account_form(self.request, driver_name)
            form.redirect = router.base_url()

        else:
            raise ValueError('Unsupported form type')

        if not form.redirect:
            form.redirect = router.base_url()

        metatag.t_set('title', form.title)

        tpl_args = {
            'driver': driver_name,
            'form_type': form_type,
            'form': form,
        }

        try:
            return router.call('auth_ui_form', tpl_args)
        except routing.error.RuleNotFound:
            return tpl.render('auth_ui/form', tpl_args)


class SignUpConfirm(routing.Controller):
    """Confirm Sign Up
    """

    def exec(self):
        try:
            user = next(auth.find_users(query.Query(query.Eq('confirmation_hash', self.arg('code')))))
        except StopIteration:
            return self.redirect(self.arg('__redirect', _api.sign_in_url()))

        try:
            auth.switch_user_to_system()
            user.confirmation_hash = None
            if user.status == auth.USER_STATUS_WAITING:
                user.status = auth.get_new_user_status()
            user.save()
        finally:
            auth.restore_user()

        router.session().add_success_message(lang.t('auth_ui@registration_confirm_success'))

        return self.redirect(self.arg('__redirect', _api.sign_in_url()))


class SignOut(routing.Controller):
    """Sign Out
    """

    def exec(self):
        auth.sign_out(auth.get_current_user())

        return self.redirect(self.arg('__redirect', router.base_url()))


class UserProfileView(routing.Controller):
    """User Profile View
    """

    def __init__(self):
        super().__init__()

        self.args.add_validation('nickname', auth.user_nickname_rule)

    def exec(self) -> str:
        try:
            user = auth.get_user(nickname=self.arg('nickname'))
        except auth.error.UserNotFound:
            raise self.not_found()

        if not user.is_active:
            raise self.not_found()

        c_user = auth.get_current_user()
        if not user.is_public and not (c_user == user or c_user.is_admin):
            raise self.not_found()

        self.args['user'] = user
        metatag.t_set('title', lang.t('auth_ui@profile_view_title', {'name': user.first_last_name}))

        try:
            return router.call('auth_ui_user_profile_view', self.args)
        except routing.error.RuleNotFound:
            return tpl.render('auth_ui/user-profile-view', self.args)


class UserProfileModify(routing.Controller):
    """User Profile Edit Form
    """

    def __init__(self):
        super().__init__()

        self.args.add_validation('nickname', auth.user_nickname_rule)

    def exec(self) -> str:
        try:
            self.args['form'] = _api.user_form(self.request, auth.get_user(nickname=self.arg('nickname')).uid)
        except auth.error.UserNotFound:
            raise self.not_found()

        metatag.t_set('title', lang.t('auth_ui@profile_edit_title'))

        try:
            return router.call('auth_ui_user_profile_modify', self.args)
        except routing.error.RuleNotFound:
            return tpl.render('auth_ui/user-profile-modify', self.args)
