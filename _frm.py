"""PytSite Auth UI Plugin Forms
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import validation, errors, router, lang
from plugins import form, auth, widget, file_ui, permissions
from . import _widget


class Role(form.Form):
    def _on_setup_form(self):
        if not self.attr('role_uid'):
            raise RuntimeError("Form's attribute 'role_uid' was not provided")

        if not auth.get_current_user().is_admin:
            raise errors.ForbidOperation()

        self.name = 'auth_ui_role'
        self.css += ' auth-ui-form-role'

    def _on_setup_widgets(self):
        role_uid = self.attr('role_uid')
        role = auth.get_role(uid=role_uid) if role_uid != '0' else None

        self.add_widget(widget.input.Text(
            uid='name',
            value=role.name if role else None,
            label=self.t('name'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))
        self.add_rule('name', auth.validation.AuthEntityFieldUnique(
            e_type='role',
            field_name='name',
            exclude_uids=role.uid if role else None,
        ))

        self.add_widget(widget.input.Text(
            uid='description',
            value=role.description if role else None,
            label=self.t('description'),
            required=True,
            enabled=role.name not in ('anonymous', 'user') if role else True,
        ))

        # Permissions tabs
        perms_tabs = widget.select.Tabs(
            uid='permissions',
            label=self.t('permissions')
        )

        # Permissions tabs content
        for g_name, g_desc in sorted(permissions.get_permission_groups().items(), key=lambda x: x[0]):
            if g_name == 'auth':
                continue

            perms = permissions.get_permissions(g_name)
            if not perms:
                continue

            # Tab
            tab_id = 'permissions-' + g_name
            perms_tabs.add_tab(tab_id, lang.t(g_desc))

            # Tab's content
            perms_tabs.add_widget(widget.select.Checkboxes(
                uid='permission-checkboxes-' + tab_id,
                name='permissions',
                items=[(p[0], lang.t(p[1])) for p in perms],
                value=role.permissions if role else [],
            ), tab_id)

        self.add_widget(perms_tabs)

        # "Cancel" button
        self.add_widget(widget.button.Link(
            uid='action_cancel',
            weight=100,
            form_area='footer',
            icon='fa fas fa-fw fa-ban',
            value=self.t('cancel'),
            href=self.referer or self.redirect or router.base_url(),
        ))

    def _on_submit(self):
        role_uid = self.attr('role_uid')

        if role_uid == '0':
            role = auth.create_role(self.val('name'), self.val('description'))
        else:
            role = auth.get_role(uid=role_uid)

        for k, v in self.values.items():
            if role.has_field(k):
                role.set_field(k, v)

        role.save()


class User(form.Form):
    def _on_setup_form(self):
        user_uid = self.attr('user_uid')
        if not user_uid:
            raise ValueError("Form's attribute 'user_uid' was not provided")

        c_user = auth.get_current_user()

        # Only profile owners and admins can modify profiles
        if user_uid != '0':
            user = auth.get_user(uid=self.attr('user_uid'))
            if not (c_user.is_admin or c_user == user):
                raise errors.ForbidOperation()

        # Only admins can create new users
        elif not c_user.is_admin:
            raise errors.ForbidOperation()

        self.name = 'auth_ui_user'
        self.css += ' auth-ui-form-user'
        self.area_footer_css += ' text-center'

    def _on_setup_widgets(self):
        user_uid = self.attr('user_uid')
        user = auth.get_user(uid=user_uid) if user_uid != '0' else None
        c_user = auth.get_current_user()

        row_1 = self.add_widget(widget.container.Card(
            uid='row_1',
            header=self.t('registration_info'),
            body_css='row',
        ))

        row_1_left = row_1.append_child(widget.container.Container(
            uid='row_1_left',
            css='col-xs-12 col-12 col-sm-4 col-md-2',
        ))

        row_1_center = row_1.append_child(widget.container.Container(
            uid='row_1_center',
            css='col-xs-12 col-12 col-sm-4 col-md-5',
        ))

        row_1_right = row_1.append_child(widget.container.Container(
            uid='row_1_right',
            css='col-xs-12 col-12 col-sm-4 col-md-5',
        ))

        # Picture
        row_1_left.append_child(file_ui.widget.ImagesUpload(
            uid='picture',
            value=user.picture if user else None,
            max_file_size=3,
            label=self.t('photo'),
        ))

        # Login
        row_1_center.append_child(widget.input.Email(
            uid='login',
            value=user.login if user else None,
            label=self.t('email'),
            required=True,
            enabled=c_user.is_admin,
            max_length=auth.LOGIN_MAX_LENGTH,
        ))
        self.add_rule('login', auth.validation.AuthEntityFieldUnique(
            e_type='user',
            field_name='login',
            exclude_uids=user.uid if user else None,
        ))

        # Nickname
        row_1_center.append_child(widget.input.Text(
            uid='nickname',
            value=user.nickname if user else None,
            label=self.t('nickname'),
            required=True,
            max_length=auth.NICKNAME_MAX_LENGTH,
        ))
        self.add_rules('nickname', (
            auth.user_nickname_rule,
            auth.validation.AuthEntityFieldUnique(
                e_type='user',
                field_name='nickname',
                exclude_uids=user.uid if user else None,
            )
        ))

        # Birth date
        row_1_center.append_child(widget.select.DateTime(
            uid='birth_date',
            value=user.birth_date if user else None,
            label=self.t('birth_date'),
            timepicker=False,
        ))

        # Gender
        row_1_center.append_child(widget.select.Select(
            uid='gender',
            value=user.gender if user else None,
            label=self.t('gender'),
            items=[
                ('m', self.t('male')),
                ('f', self.t('female')),
            ]
        ))

        # First name
        row_1_right.append_child(widget.input.Text(
            uid='first_name',
            value=user.first_name if user else None,
            label=self.t('first_name'),
            required=True,
            max_length=auth.FIRST_NAME_MAX_LENGTH,
        ))

        # Middle name
        row_1_right.append_child(widget.input.Text(
            uid='middle_name',
            value=user.middle_name if user else None,
            label=self.t('middle_name'),
            max_length=auth.MIDDLE_NAME_MAX_LENGTH,
        ))

        # Last name
        row_1_right.append_child(widget.input.Text(
            uid='last_name',
            value=user.last_name if user else None,
            label=self.t('last_name'),
            max_length=auth.LAST_NAME_MAX_LENGTH,
        ))

        # Position
        row_1_right.append_child(widget.input.Text(
            uid='position',
            value=user.position if user else None,
            label=self.t('position'),
            max_length=auth.USER_POSITION_MAX_LENGTH,
        ))

        # Row 2
        row_2 = self.add_widget(widget.container.Container(
            uid='row_2',
            body_css='row',
        ))

        # Row 2 left
        row_2_left = row_2.append_child(widget.container.Container(
            uid='row_2_left',
            css='col-xs-12 col-12 col-sm-6 col-lg-8',
        ))

        # Contact info
        contact = row_2_left.append_child(widget.container.Card(
            uid='contact',
            body_css='row',
            header=self.t('contact_info'),
        ))

        # Contact info left
        contact_left = contact.append_child(widget.container.Container(
            uid='contact_left',
            css='col-xs-12 col-12 col-lg-6'
        ))

        # Country
        contact_left.append_child(widget.input.Text(
            uid='country',
            value=user.country if user else None,
            label=self.t('country'),
            max_length=auth.COUNTRY_MAX_LENGTH,
        ))

        # Province
        contact_left.append_child(widget.input.Text(
            uid='province',
            value=user.province if user else None,
            label=self.t('province'),
            max_length=auth.PROVINCE_MAX_LENGTH,
        ))

        # City
        contact_left.append_child(widget.input.Text(
            uid='city',
            value=user.city if user else None,
            label=self.t('city'),
            max_length=auth.CITY_MAX_LENGTH,
        ))

        # District
        contact_left.append_child(widget.input.Text(
            uid='district',
            value=user.district if user else None,
            label=self.t('district'),
            max_length=auth.DISTRICT_MAX_LENGTH,
        ))

        # Contact info right
        contact_right = contact.append_child(widget.container.Container(
            uid='contact_right',
            css='col-xs-12 col-12 col-lg-6'
        ))

        # Street
        contact_right.append_child(widget.input.Text(
            uid='street',
            value=user.street if user else None,
            label=self.t('street'),
            max_length=auth.STREET_MAX_LENGTH,
        ))

        # House number
        contact_right.append_child(widget.input.Text(
            uid='building',
            value=user.building if user else None,
            label=self.t('building'),
            max_length=auth.BUILDING_MAX_LENGTH,
        ))

        # Apt number
        contact_right.append_child(widget.input.Text(
            uid='apt_number',
            value=user.apt_number if user else None,
            label=self.t('apt_number'),
            max_length=auth.APT_NUMBER_MAX_LENGTH,
        ))

        # Phone
        contact_right.append_child(widget.input.Text(
            uid='phone',
            value=user.phone if user else None,
            label=self.t('phone'),
            max_length=auth.PHONE_MAX_LENGTH,
        ))

        # URLs
        contact.append_child(widget.input.StringList(
            uid='urls',
            value=user.urls if user else None,
            label=self.t('social_links'),
            max_rows=10,
            add_btn_label=self.t('add_link'),
            css='col-xs-12 col-12',
        ))
        self.add_rule('urls', validation.rule.Url())

        # Row 2 right
        row_2_right = row_2.append_child(widget.container.Container(
            uid='row_2_right',
            css='col-xs-12 col-12 col-sm-6 col-lg-4',
        ))

        # Cover picture card
        cover_picture_card = row_2_right.append_child(widget.container.Card(
            uid='cover_picture_card',
            header=self.t('cover_picture'),
        ))

        # Cover picture
        cover_picture_card.append_child(file_ui.widget.ImagesUpload(
            uid='cover_picture',
            thumb_width=1200,
            thumb_height=450,
            max_file_size=5,
            value=user.cover_picture if user else None,
        ))

        # Security card
        security = row_2_right.append_child(widget.container.Card(
            uid='security',
            header=self.t('security'),
        ))

        # User account confirmed
        if c_user.is_admin and auth.is_sign_up_confirmation_required():
            security.append_child(widget.select.Checkbox(
                uid='is_confirmed',
                value=user.is_confirmed if (user and user.is_confirmed) else None,
                label=self.t('user_account_is_confirmed'),
            ))

        # Profile is public
        security.append_child(widget.select.Checkbox(
            uid='is_public',
            value=user.is_public if user else None,
            label=self.t('this_is_public_profile'),
        ))

        # New password
        security.append_child(widget.input.Password(
            uid='password',
            label=self.t('new_password'),
            autocomplete='new-password',
        ))

        # New password confirm
        security.append_child(widget.input.Password(
            uid='password_confirm',
            label=self.t('new_password_confirmation'),
            autocomplete='new-password',
        ))

        # Row 3
        row_3 = self.add_widget(widget.container.Card(
            uid='row_3',
            header=self.t('about_yourself'),
        ))

        # Description
        row_3.append_child(widget.input.TextArea(
            uid='description',
            value=user.description if user else '',
            max_length=auth.USER_DESCRIPTION_MAX_LENGTH,
        ))

        # Row 4
        if c_user.is_admin:
            admin = self.add_widget(widget.container.Card(
                uid='admin',
                header=self.t('administration'),
                body_css='row',
            ))

            admin.append_child(widget.select.Select(
                uid='status',
                value=user.status if user else auth.get_new_user_status(),
                label=self.t('status'),
                items=auth.get_user_statuses(),
                required=True,
                append_none_item=False,
                css='col-xs-12 col-12 col-md-3'
            ))

            admin.append_child(_widget.RolesCheckboxes(
                uid='roles',
                value=user.roles if user else [auth.get_role(r) for r in auth.get_new_user_roles()],
                label=self.t('roles'),
                css='col-xs-12 col-12 col-md-3'
            ))

        # "Cancel" button
        self.add_widget(widget.button.Link(
            uid='action_cancel',
            weight=100,
            form_area='footer',
            icon='fa fas fa-fw fa-ban',
            value=self.t('cancel'),
            href=self.referer or self.redirect or router.base_url(),
        ))

    def _on_validate(self):
        errs = {}

        if self.val('password') and (self.val('password') != self.val('password_confirm')):
            err_msg = self.t('passwords_not_match')
            errs.update({
                'password': err_msg,
                'password_confirm': err_msg,
            })

        if errs:
            raise form.FormValidationError(errs)

    def _on_submit(self):
        user_uid = self.attr('user_uid')
        c_user = auth.get_current_user()

        if user_uid == '0':
            user = auth.create_user(self.val('login'), self.val('password'))
        else:
            user = auth.get_user(uid=user_uid)

        for k, v in self.values.items():
            if not user.has_field(k):
                continue

            if k in ('login', 'status', 'roles') and not c_user.is_admin:
                continue

            user.set_field(k, v)

        user.save()

        if not self.redirect:
            self.redirect = router.rule_url('auth_ui@user_profile_view', {'nickname': user.nickname})
