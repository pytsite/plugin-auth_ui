"""PytSite Auth UI Plugin Widgets
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Union as _Union, List as _List, Tuple as _Tuple
from pytsite import lang as _lang
from plugins import widget as _widget, auth as _auth, query as _query


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
            raise TypeError('List or tuple expected.')

        clean_value = []
        for role in value:
            if isinstance(role, _auth.model.AbstractRole):
                clean_value.append(role.uid)
            elif isinstance(role, str):
                clean_value.append(role)
            else:
                raise TypeError('List of roles or UIDs expected.')

        super().set_val(clean_value)


class UserSelect(_widget.select.Select):
    """User Select Widget
    """

    def __init__(self, uid: str, **kwargs):
        super().__init__(uid, **kwargs)

        c_user = _auth.get_current_user()
        if not c_user.is_admin_or_dev:
            self._items.append((c_user.uid, '{} ({})'.format(c_user.full_name, c_user.login)))
        else:
            for user in _auth.find_users(_query.Query(_query.Eq('status', 'active')), [('first_name', 1)]):
                self._items.append((user.uid, '{} ({})'.format(user.full_name, user.login)))

    def set_val(self, value):
        if isinstance(value, _auth.model.AbstractUser):
            value = value.uid
        elif isinstance(value, str):
            # Check user existence
            _auth.get_user(uid=value)
        elif value is not None:
            raise TypeError('User object, UID or None expected, got {}.'.format(value))

        return super().set_val(value)

    def get_val(self, **kwargs) -> _auth.model.AbstractUser:
        value = super().get_val(**kwargs)
        if value:
            value = _auth.get_user(uid=value)

        return value
