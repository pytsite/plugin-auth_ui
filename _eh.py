"""PytSite Auth UI Plugin Events Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import router, lang, mail, tpl
from plugins import auth


def on_auth_sign_up(user: auth.AbstractUser):
    # Set session notification
    router.session().add_success_message(lang.t('auth_ui@registration_form_success'))

    # Send a confirmation email to the user
    if auth.is_sign_up_confirmation_required():
        msg = tpl.render('auth_ui@mail/{}/sign-up'.format(lang.get_current()), {
            'user': user,
            'confirm_url': router.rule_url('auth_ui@sign_up_confirm',
                                           {'code': user.confirmation_hash}) if not user.is_confirmed else None
        })
        mail.Message(user.login, lang.t('auth_ui@confirm_registration'), msg).send()

    # Send a notification emails to admins
    if auth.is_sign_up_admins_notification_enabled():
        for admin in auth.get_admin_users():
            msg = tpl.render('auth_ui@mail/{}/sign-up-admin-notify'.format(lang.get_current()), {
                'admin': admin,
                'user': user,
            })
            mail.Message(admin.login, lang.t('auth_ui@registration_admin_notify'), msg).send()


def on_auth_user_status_change(user: auth.AbstractUser, status: str):
    if auth.is_user_status_change_notification_enabled():
        msg = tpl.render('auth_ui@mail/{}/user-status-change'.format(lang.get_current()), {
            'user': user,
            'status': status,
        })
        mail.Message(user.login, lang.t('auth_ui@user_status_change_notify'), msg).send()


def on_auth_user_as_jsonable(user: auth.AbstractUser, data: dict):
    if user.is_public:
        data['url'] = router.rule_url('auth_ui@user_profile_view', {'nickname': user.nickname})
