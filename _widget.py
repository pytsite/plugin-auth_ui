"""PytSite Auth UI Plugin Widgets
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json as _json
from typing import Union as _Union, List as _List, Tuple as _Tuple
from pytsite import lang as _lang, html as _html
from plugins import widget as _widget, auth as _auth, http_api as _http_api


class RolesCheckboxes(_widget.select.Checkboxes):
    """Roles Checkboxes Widget
    """

    def __init__(self, uid: str, **kwargs):
        """Init
        """
        items = []
        for role in _auth.find_roles():
            if role.name == 'anonymous':
                continue

            role_desc = role.description
            try:
                role_desc = _lang.t(role_desc)
            except _lang.error.Error:
                pass

            items.append((role.uid, role_desc))

        super().__init__(uid, items=items, **kwargs)

    def set_val(self, value: _Union[_List, _Tuple]):
        """Set value of the widget.
        """
        if not isinstance(value, (list, tuple)):
            raise TypeError('List or tuple expected')

        clean_value = []
        for role in value:
            if isinstance(role, _auth.model.AbstractRole):
                clean_value.append(role.uid)
            elif isinstance(role, str):
                clean_value.append(role)
            else:
                raise TypeError('List of roles or UIDs expected.')

        super().set_val(clean_value)


class UserSelect(_widget.select.Select2):
    """User Select Widget
    """

    def __init__(self, uid: str, **kwargs):
        kwargs.setdefault('ajax_url', _http_api.url('auth_ui@get_widget_user_select'))
        kwargs.setdefault('minimum_input_length', 3)

        super().__init__(uid, **kwargs)

    def set_val(self, value):
        if isinstance(value, _auth.model.AbstractUser):
            value = value.uid
        elif isinstance(value, str):
            if value.strip():
                # Check user existence
                _auth.get_user(uid=value)
            else:
                value = None

        if value is not None:
            raise TypeError('User object, UID or None expected, got {}'.format(value))

        return super().set_val(value)

    def get_val(self, **kwargs) -> _auth.model.AbstractUser:
        value = super().get_val(**kwargs)
        if value:
            value = _auth.get_user(uid=value)

        return value

    def _get_element(self, **kwargs) -> _html.Element:
        value = self.get_val(**kwargs)

        if value:
            text = value.first_last_name
            if _auth.get_current_user().is_admin:
                text += ' ({})'.format(value.login)

            self._items.append([value.uid, text])

        return super()._get_element(**kwargs)


class UsersSlots(_widget.Abstract):
    def __init__(self, uid: str, **kwargs):
        super().__init__(uid, **kwargs)

        self._max_slots = kwargs.get('max_slots', 100)
        self._modal_title = kwargs.get('modal_title', _lang.t('auth_ui@select_user'))
        self._modal_ok_button_caption = kwargs.get('modal_ok_button_caption', _lang.t('auth_ui@add'))
        self._modal_cancel_button_caption = kwargs.get('modal_cancel_button_caption')

    def _get_element(self, **kwargs) -> _html.Element:
        self.data.update({
            'value': _json.dumps([u.uid for u in (self.value or [])]),
            'max_slots': self._max_slots,
            'modal_title': self._modal_title,
            'modal_ok_button_caption': self._modal_ok_button_caption,
            'modal_cancel_button_caption': self._modal_cancel_button_caption,
        })

        return _html.Div(css='widget-component')
