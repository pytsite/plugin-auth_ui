"""PytSite Auth UI Plugin Forms
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import validation as _validation, errors as _errors, router as _router, lang as _lang
from plugins import form as _form, auth as _auth, widget as _widget, file_ui as _file_ui, permissions as _permissions
from . import _widget as _w


class Role(_form.Form):
    def _on_setup_form(self):
        if not self.attr('role_uid'):
            raise RuntimeError("Form's attribute 'role_uid' was not provided")

        if not _auth.get_current_user().is_admin:
            raise _errors.ForbidOperation()

        self.name = 'auth_ui_role'
        self.css += ' auth-ui-form-role'

    def _on_setup_widgets(self):
        role_uid = self.attr('role_uid')
        role = _auth.get_role(uid=role_uid) if role_uid != '0' else None

        self.add_widget(_widget.input.Text(
            uid='name',
            value=role.name if role else None,
            label=self.t('name'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))
        self.add_rule('name', _auth.validation.AuthEntityFieldUnique(
            e_type='role',
            field_name='name',
            exclude_uids=role.uid if role else None,
        ))

        self.add_widget(_widget.input.Text(
            uid='description',
            value=role.description if role else None,
            label=self.t('description'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))

        # Permissions tabs
        perms_tabs = _widget.select.Tabs(
            uid='permissions',
            label=self.t('permissions')
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
            weight=100,
            form_area='footer',
            icon='fa fas fa-fw fa-ban',
            value=self.t('cancel'),
            href=self.referer or self.redirect or _router.base_url(),
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
            raise ValueError("Form's attribute 'user_uid' was not provided")

        c_user = _auth.get_current_user()

        # Only profile owners and admins can modify profiles
        if user_uid != '0':
            user = _auth.get_user(uid=self.attr('user_uid'))
            if not (c_user.is_admin or c_user == user):
                raise _errors.ForbidOperation()

        # Only admins can create new users
        elif not c_user.is_admin:
            raise _errors.ForbidOperation()

        self.name = 'auth_ui_user'
        self.css += ' auth-ui-form-user'
        self.assets.extend(['auth_ui@css/form.css'])
        self.area_footer_css += ' text-center'

    def _on_setup_widgets(self):
        user_uid = self.attr('user_uid')
        user = _auth.get_user(uid=user_uid) if user_uid != '0' else None
        c_user = _auth.get_current_user()

        row_1 = self.add_widget(_widget.container.Card(
            uid='row_1',
            header=self.t('registration_info'),
            body_css='row',
        ))

        row_1_left = row_1.append_child(_widget.container.Container(
            uid='row_1_left',
            css='col-xs-12 col-12 col-sm-4 col-md-2',
        ))

        row_1_center = row_1.append_child(_widget.container.Container(
            uid='row_1_center',
            css='col-xs-12 col-12 col-sm-4 col-md-5',
        ))

        row_1_right = row_1.append_child(_widget.container.Container(
            uid='row_1_right',
            css='col-xs-12 col-12 col-sm-4 col-md-5',
        ))

        # Picture
        row_1_left.append_child(_file_ui.widget.ImagesUpload(
            uid='picture',
            value=user.picture if user else None,
            max_file_size=3,
            label=self.t('photo'),
        ))

        # Login
        row_1_center.append_child(_widget.input.Email(
            uid='login',
            value=user.login if user else None,
            label=self.t('email'),
            required=True,
            enabled=c_user.is_admin,
            max_length=_auth.LOGIN_MAX_LENGTH,
        ))
        self.add_rule('login', _auth.validation.AuthEntityFieldUnique(
            e_type='user',
            field_name='login',
            exclude_uids=user.uid if user else None,
        ))

        # Nickname
        row_1_center.append_child(_widget.input.Text(
            uid='nickname',
            value=user.nickname if user else None,
            label=self.t('nickname'),
            required=True,
            max_length=_auth.NICKNAME_MAX_LENGTH,
        ))
        self.add_rules('nickname', (
            _auth.user_nickname_rule,
            _auth.validation.AuthEntityFieldUnique(
                e_type='user',
                field_name='nickname',
                exclude_uids=user.uid if user else None,
            )
        ))

        # Birth date
        row_1_center.append_child(_widget.select.DateTime(
            uid='birth_date',
            value=user.birth_date if user else None,
            label=self.t('birth_date'),
            timepicker=False,
        ))

        # Gender
        row_1_center.append_child(_widget.select.Select(
            uid='gender',
            value=user.gender if user else None,
            label=self.t('gender'),
            items=[
                ('m', self.t('male')),
                ('f', self.t('female')),
            ]
        ))

        # First name
        row_1_right.append_child(_widget.input.Text(
            uid='first_name',
            value=user.first_name if user else None,
            label=self.t('first_name'),
            required=True,
            max_length=_auth.FIRST_NAME_MAX_LENGTH,
        ))

        # Middle name
        row_1_right.append_child(_widget.input.Text(
            uid='middle_name',
            value=user.middle_name if user else None,
            label=self.t('middle_name'),
            max_length=_auth.MIDDLE_NAME_MAX_LENGTH,
        ))

        # Last name
        row_1_right.append_child(_widget.input.Text(
            uid='last_name',
            value=user.last_name if user else None,
            label=self.t('last_name'),
            max_length=_auth.LAST_NAME_MAX_LENGTH,
        ))

        # Position
        row_1_right.append_child(_widget.input.Text(
            uid='position',
            value=user.position if user else None,
            label=self.t('position'),
            max_length=_auth.USER_POSITION_MAX_LENGTH,
        ))

        # Row 2
        row_2 = self.add_widget(_widget.container.Container(
            uid='row_2',
            body_css='row',
        ))

        # Row 2 left
        row_2_left = row_2.append_child(_widget.container.Container(
            uid='row_2_left',
            css='col-xs-12 col-12 col-sm-6 col-lg-8',
        ))

        # Contact info
        contact = row_2_left.append_child(_widget.container.Card(
            uid='contact',
            body_css='row',
            header=self.t('contact_info'),
        ))

        # Contact info left
        contact_left = contact.append_child(_widget.container.Container(
            uid='contact_left',
            css='col-xs-12 col-12 col-lg-6'
        ))

        # Country
        contact_left.append_child(_widget.input.Text(
            uid='country',
            value=user.country if user else None,
            label=self.t('country'),
            max_length=_auth.COUNTRY_MAX_LENGTH,
        ))

        # Postal code
        contact_left.append_child(_widget.input.Text(
            uid='postal_code',
            value=user.postal_code if user else None,
            label=self.t('postal_code'),
            max_length=_auth.POSTAL_CODE_MAX_LENGTH,
        ))

        # Region
        contact_left.append_child(_widget.input.Text(
            uid='region',
            value=user.region if user else None,
            label=self.t('region'),
            max_length=_auth.REGION_MAX_LENGTH,
        ))

        # City
        contact_left.append_child(_widget.input.Text(
            uid='city',
            value=user.city if user else None,
            label=self.t('city'),
            max_length=_auth.CITY_MAX_LENGTH,
        ))

        # Contact info right
        contact_right = contact.append_child(_widget.container.Container(
            uid='contact_right',
            css='col-xs-12 col-12 col-lg-6'
        ))

        # Street
        contact_right.append_child(_widget.input.Text(
            uid='street',
            value=user.street if user else None,
            label=self.t('street'),
            max_length=_auth.STREET_MAX_LENGTH,
        ))

        # House number
        contact_right.append_child(_widget.input.Text(
            uid='house_number',
            value=user.house_number if user else None,
            label=self.t('house_number'),
            max_length=_auth.HOUSE_NUMBER_MAX_LENGTH,
        ))

        # Apt number
        contact_right.append_child(_widget.input.Text(
            uid='apt_number',
            value=user.apt_number if user else None,
            label=self.t('apt_number'),
            max_length=_auth.APT_NUMBER_MAX_LENGTH,
        ))

        # Phone
        contact_right.append_child(_widget.input.Text(
            uid='phone',
            value=user.phone if user else None,
            label=self.t('phone'),
            max_length=_auth.PHONE_MAX_LENGTH,
        ))

        # URLs
        contact.append_child(_widget.input.StringList(
            uid='urls',
            value=user.urls if user else None,
            label=self.t('social_links'),
            max_rows=10,
            add_btn_label=self.t('add_link'),
            css='col-xs-12 col-12',
            unique=True,
        ))
        self.add_rule('urls', _validation.rule.Url())

        # Row 2 right
        row_2_right = row_2.append_child(_widget.container.Container(
            uid='row_2_right',
            css='col-xs-12 col-12 col-sm-6 col-lg-4',
        ))

        # Cover picture card
        cover_picture_card = row_2_right.append_child(_widget.container.Card(
            uid='cover_picture_card',
            header=self.t('cover_picture'),
        ))

        # Cover picture
        cover_picture_card.append_child(_file_ui.widget.ImagesUpload(
            uid='cover_picture',
            thumb_width=1200,
            thumb_height=450,
            max_file_size=5,
            value=user.cover_picture if user else None,
        ))

        # Security card
        security = row_2_right.append_child(_widget.container.Card(
            uid='security',
            header=self.t('security'),
        ))

        # User account confirmed
        if c_user.is_admin and _auth.is_sign_up_confirmation_required():
            security.append_child(_widget.select.Checkbox(
                uid='is_confirmed',
                value=user.is_confirmed if (user and user.is_confirmed) else None,
                label=self.t('user_account_is_confirmed'),
            ))

        # Profile is public
        security.append_child(_widget.select.Checkbox(
            uid='is_public',
            value=user.is_public if user else None,
            label=self.t('this_is_public_profile'),
        ))

        # New password
        security.append_child(_widget.input.Password(
            uid='password',
            label=self.t('new_password'),
            autocomplete='off',
        ))

        # New password confirm
        security.append_child(_widget.input.Password(
            uid='password_confirm',
            label=self.t('new_password_confirmation'),
            autocomplete='off',
        ))

        # Row 3
        row_3 = self.add_widget(_widget.container.Card(
            uid='row_3',
            header=self.t('about_yourself'),
        ))

        # Description
        row_3.append_child(_widget.input.TextArea(
            uid='description',
            value=user.description if user else None,
            max_length=_auth.USER_DESCRIPTION_MAX_LENGTH,
        ))

        # Row 4
        if c_user.is_admin:
            admin = self.add_widget(_widget.container.Card(
                uid='admin',
                header=self.t('administration'),
                body_css='row',
            ))

            admin.append_child(_widget.select.Select(
                uid='status',
                value=user.status if user else _auth.get_new_user_status(),
                label=self.t('status'),
                items=_auth.get_user_statuses(),
                required=True,
                append_none_item=False,
                css='col-xs-12 col-12 col-md-3'
            ))

            admin.append_child(_w.RolesCheckboxes(
                uid='roles',
                value=user.roles if user else [_auth.get_role(r) for r in _auth.get_new_user_roles()],
                label=self.t('roles'),
                css='col-xs-12 col-12 col-md-3'
            ))

        # "Cancel" button
        self.add_widget(_widget.button.Link(
            uid='action_cancel',
            weight=100,
            form_area='footer',
            icon='fa fas fa-fw fa-ban',
            value=self.t('cancel'),
            href=self.referer or self.redirect or _router.base_url(),
        ))

    def _on_validate(self):
        errors = {}

        if self.val('password') and (self.val('password') != self.val('password_confirm')):
            err_msg = self.t('passwords_not_match')
            errors.update({
                'password': err_msg,
                'password_confirm': err_msg,
            })

        if errors:
            raise _form.FormValidationError(errors)

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

        if not self.redirect:
            self.redirect = _router.rule_url('auth_ui@user_profile_view', {'nickname': user.nickname})
