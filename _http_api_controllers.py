"""Spilno HTTP API Controllers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import routing as _routing
from plugins import auth as _auth, query as _query


class GetWidgetUserSelect(_routing.Controller):
    def _get_query(self) -> _query.Query:
        q = _query.Query()

        if not _auth.get_current_user().is_admin:
            q.add(_query.Eq('status', 'active'))
            q.add(_query.Eq('profile_is_public', True))

        search = self.arg('q')
        if search:
            q.add(_query.Or([
                _query.Regex('first_name', search, True),
                _query.Regex('last_name', search, True),
            ]))

        return q

    @staticmethod
    def _format_option_text(user: _auth.AbstractUser) -> str:
        r = user.first_last_name

        if _auth.get_current_user().is_admin:
            r += ' ({})'.format(user.login)

        return r

    def exec(self):
        c_user = _auth.get_current_user()
        if c_user.is_anonymous:
            raise self.forbidden()

        skip = self.arg('skip', 0)

        limit = self.arg('limit', 10)
        if limit > 100:
            limit = 100

        f = _auth.find_users(self._get_query(), [('first_name', 1)], limit, skip)

        return {
            'results': [{'id': u.uid, 'text': self._format_option_text(u)} for u in f]
        }
