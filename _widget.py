"""PytSite Auth UI Plugin Widgets
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json
import htmler
from typing import Union, List, Tuple
from pytsite import lang
from plugins import widget, auth, http_api


class RolesCheckboxes(widget.select.Checkboxes):
    """Roles Checkboxes Widget
    """

    def __init__(self, uid: str, **kwargs):
        """Init
        """
        items = []
        for role in auth.find_roles():
            if role.name == 'anonymous':
                continue

            role_desc = role.description
            try:
                role_desc = lang.t(role_desc)
            except lang.error.Error:
                pass

            items.append((role.uid, role_desc))

        super().__init__(uid, items=items, **kwargs)

    def set_val(self, value: Union[List, Tuple]):
        """Set value of the widget.
        """
        if not isinstance(value, (list, tuple)):
            raise TypeError('List or tuple expected')

        clean_value = []
        for role in value:
            if isinstance(role, auth.model.AbstractRole):
                clean_value.append(role.uid)
            elif isinstance(role, str):
                clean_value.append(role)
            else:
                raise TypeError('List of roles or UIDs expected.')

        super().set_val(clean_value)


class UserSelect(widget.select.Select2):
    """User Select Widget
    """

    def __init__(self, uid: str, **kwargs):
        kwargs.setdefault('ajax_url', http_api.url('auth_ui@get_widget_user_select'))
        kwargs.setdefault('minimum_input_length', 3)

        super().__init__(uid, **kwargs)

    def set_val(self, value):
        if isinstance(value, auth.model.AbstractUser):
            value = value.uid
        elif isinstance(value, str):
            value = value.strip()
            value = auth.get_user(uid=value).uid if value else None
        elif value is not None:
            raise TypeError('User object, str or None expected, not {}'.format(repr(value)))

        return super().set_val(value)

    def get_val(self, **kwargs) -> auth.model.AbstractUser:
        value = super().get_val(**kwargs)
        if value:
            value = auth.get_user(uid=value)

        return value

    def _get_element(self, **kwargs) -> htmler.Element:
        value = self.get_val(**kwargs)

        if value:
            text = value.first_last_name
            if auth.get_current_user().is_admin:
                text += ' ({})'.format(value.login)

            self._items.append([value.uid, text])

        return super()._get_element(**kwargs)


class UsersSlots(widget.Abstract):
    def __init__(self, uid: str, **kwargs):
        super().__init__(uid, **kwargs)

        self._max_slots = kwargs.get('max_slots', 100)
        self._modal_title = kwargs.get('modal_title', lang.t('auth_ui@select_user'))
        self._modal_ok_button_caption = kwargs.get('modal_ok_button_caption', lang.t('auth_ui@add'))
        self._modal_cancel_button_caption = kwargs.get('modal_cancel_button_caption')

    def _get_element(self, **kwargs) -> htmler.Element:
        self.data.update({
            'value': json.dumps([u.uid for u in (self.value or [])]),
            'max_slots': self._max_slots,
            'modal_title': self._modal_title,
            'modal_ok_button_caption': self._modal_ok_button_caption,
            'modal_cancel_button_caption': self._modal_cancel_button_caption,
        })

        return htmler.Div(css='widget-component')
