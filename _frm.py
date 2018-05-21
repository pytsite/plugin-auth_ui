"""PytSite Auth UI Plugin Forms
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import validation as _validation, lang as _lang, errors as _errors
from plugins import form as _form, auth as _auth, widget as _widget, file_ui as _file_ui, permissions as _permissions
from . import _widget as _w


class Role(_form.Form):
    def _on_setup_form(self):
        if not self.attr('role_uid'):
            raise RuntimeError("Form's attribute 'role_uid' was not provided")

        if not _auth.get_current_user().is_admin:
            raise _errors.ForbidOperation()

        self.css += ' auth-ui-form-role'

    def _on_setup_widgets(self):
        role_uid = self.attr('role_uid')
        role = _auth.get_role(uid=role_uid) if role_uid != '0' else None

        self.add_widget(_widget.input.Text(
            weight=10,
            uid='name',
            value=role.name if role else None,
            label=_lang.t('auth_ui@name'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))
        self.add_rule('name', _auth.validation.AuthEntityFieldUnique(
            e_type='role',
            field_name='name',
            exclude_uids=role.uid if role else None,
        ))

        self.add_widget(_widget.input.Text(
            weight=20,
            uid='description',
            value=role.description if role else None,
            label=_lang.t('auth_ui@description'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))

        # Permissions tabs
        perms_tabs = _widget.select.Tabs(
            uid='permissions',
            weight=30,
            label=_lang.t('auth_ui@permissions')
        )

        # Permissions tabs content
        for g_name, g_desc in sorted(_permissions.get_permission_groups().items(), key=lambda x: x[0]):
            if g_name == 'auth':
                continue

            perms = _permissions.get_permissions(g_name)
            if not perms:
                continue

            # Tab
            tab_id = 'permissions-' + g_name
            perms_tabs.add_tab(tab_id, _lang.t(g_desc))

            # Tab's content
            perms_tabs.add_widget(_widget.select.Checkboxes(
                uid='permission-checkboxes-' + tab_id,
                name='permissions',
                items=[(p[0], _lang.t(p[1])) for p in perms],
                value=role.permissions if role else [],
            ), tab_id)

        self.add_widget(perms_tabs)

        # "Cancel" button
        self.add_widget(_widget.button.Link(
            uid='action_cancel',
            weight=10,
            form_area='footer',
            icon='fa fa-ban',
            value=_lang.t('auth_ui@cancel'),
            href=self.redirect,
        ))

    def _on_submit(self):
        role_uid = self.attr('role_uid')

        if role_uid == '0':
            role = _auth.create_role(self.val('name'), self.val('description'))
        else:
            role = _auth.get_role(uid=role_uid)

        for k, v in self.values.items():
            if role.has_field(k):
                role.set_field(k, v)

        role.save()


class User(_form.Form):
    def _on_setup_form(self):
        user_uid = self.attr('user_uid')
        if not user_uid:
            raise RuntimeError("Form's attribute 'user_uid' was not provided")

        c_user = _auth.get_current_user()

        # Only profile owners and admins can modify profiles
        if user_uid != '0':
            user = _auth.get_user(uid=self.attr('user_uid'))
            if not (c_user.is_admin or c_user == user):
                raise _errors.ForbidOperation()

        # Only admins can create new users
        elif not c_user.is_admin:
            raise _errors.ForbidOperation()

        self.css += ' auth-ui-form-user'
        self.area_footer_css += ' text-center'

    def _on_setup_widgets(self):
        user_uid = self.attr('user_uid')
        user = _auth.get_user(uid=user_uid) if user_uid != '0' else None
        c_user = _auth.get_current_user()

        # Picture wrapper
        pic_wrapper = _widget.Container(
            uid='picture-wrapper',
            weight=2,
            css='col-xs-12 col-sm-4 col-lg-3',
        )
        self.add_widget(pic_wrapper)

        # Content wrapper
        content_wrapper = _widget.Container(
            uid='content-wrapper',
            weight=4,
            css='col-xs-12 col-sm-8 col-lg-9',
        )
        self.add_widget(content_wrapper)

        # Image
        pic_wrapper.append_child(_file_ui.widget.ImagesUpload(
            weight=10,
            uid='picture',
            value=user.picture if user else None,
            max_file_size=1,
            show_numbers=False,
            dnd=False,
            slot_css='col-xs-B-12 col-xs-6 col-sm-12',
        ))

        # Profile is public
        content_wrapper.append_child(_widget.select.Checkbox(
            weight=10,
            uid='is_public',
            value=user.is_public if user else None,
            label=_lang.t('auth_ui@profile_is_public'),
        ))

        # Login
        if c_user.is_admin:
            content_wrapper.append_child(_widget.input.Email(
                weight=30,
                uid='login',
                value=user.login if user else None,
                label=_lang.t('auth_ui@login'),
                required=True,
            ))

            self.add_rule('login', _auth.validation.AuthEntityFieldUnique(
                e_type='user',
                field_name='login',
                exclude_uids=user.uid if user else None,
            ))

        # Nickname
        content_wrapper.append_child(_widget.input.Text(
            weight=40,
            uid='nickname',
            value=user.nickname if user else None,
            label=_lang.t('auth_ui@nickname'),
            required=True,
        ))
        self.add_rules('nickname', (
            _auth.user_nickname_rule,
            _auth.validation.AuthEntityFieldUnique(
                e_type='user',
                field_name='nickname',
                exclude_uids=user.uid if user else None,
            )
        ))

        # First name
        content_wrapper.append_child(_widget.input.Text(
            weight=50,
            uid='first_name',
            value=user.first_name if user else None,
            label=_lang.t('auth_ui@first_name'),
            required=True,
        ))

        # Last name
        content_wrapper.append_child(_widget.input.Text(
            weight=60,
            uid='last_name',
            value=user.last_name if user else None,
            label=_lang.t('auth_ui@last_name'),
        ))

        # Email
        content_wrapper.append_child(_widget.input.Email(
            weight=70,
            uid='email',
            value=user.email if user else None,
            label=_lang.t('auth_ui@email'),
            required=True,
        ))
        self.add_rule('email', _auth.validation.AuthEntityFieldUnique(
            e_type='user',
            field_name='email',
            exclude_uids=user.uid if user else None,
        ))

        # Password
        content_wrapper.append_child(_widget.input.Password(
            weight=80,
            uid='password',
            label=_lang.t('auth_ui@new_password'),
        ))

        # Country
        content_wrapper.append_child(_widget.input.Text(
            weight=90,
            uid='country',
            value=user.country if user else None,
            label=_lang.t('auth_ui@country'),
        ))

        # City
        content_wrapper.append_child(_widget.input.Text(
            weight=100,
            uid='city',
            value=user.city if user else None,
            label=_lang.t('auth_ui@city'),
        ))

        # Description
        content_wrapper.append_child(_widget.input.TextArea(
            weight=110,
            uid='description',
            value=user.description if user else None,
            label=_lang.t('auth_ui@about_yourself'),
            max_length=1024,
        ))

        # Status
        if c_user.is_admin:
            content_wrapper.append_child(_widget.select.Select(
                weight=120,
                uid='status',
                value=user.status if user else _auth.get_new_user_status(),
                label=_lang.t('auth_ui@status'),
                items=_auth.get_user_statuses(),
                h_size='col-sm-5 col-md-4 col-lg-3',
                required=True,
                append_none_item=False,
            ))

        # URLs
        content_wrapper.append_child(_widget.input.StringList(
            weight=130,
            uid='urls',
            value=user.urls if user else None,
            label=_lang.t('auth_ui@social_links'),
            max_values=5,
            add_btn_label=_lang.t('auth_ui@add_link'),
        ))
        self.add_rule('urls', _validation.rule.Url())

        # Roles
        if c_user.is_admin:
            content_wrapper.append_child(_w.RolesCheckboxes(
                weight=140,
                uid='roles',
                value=user.roles if user else [_auth.get_role(r) for r in _auth.get_new_user_roles()],
                label=_lang.t('auth_ui@roles'),
            ))

        # "Cancel" button
        self.add_widget(_widget.button.Link(
            uid='action_cancel',
            weight=10,
            form_area='footer',
            icon='fa fa-ban',
            value=_lang.t('auth_ui@cancel'),
            href=self.redirect,
        ))

    def _on_submit(self):
        user_uid = self.attr('user_uid')
        c_user = _auth.get_current_user()

        if user_uid == '0':
            user = _auth.create_user(self.val('login'), self.val('password'))
        else:
            user = _auth.get_user(uid=user_uid)

        for k, v in self.values.items():
            if not user.has_field(k):
                continue

            if k in ('login', 'status', 'roles') and not c_user.is_admin:
                continue

            user.set_field(k, v)

        user.save()
