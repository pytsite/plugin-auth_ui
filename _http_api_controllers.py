"""Spilno HTTP API Controllers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import routing
from plugins import auth, query


class GetWidgetUserSelect(routing.Controller):
    def _get_query(self) -> query.Query:
        q = query.Query()

        if not auth.get_current_user().is_admin:
            q.add(query.Eq('status', 'active'))
            q.add(query.Eq('is_public', True))

        search = self.arg('q')
        if search:
            q.add(query.Or([
                query.Regex('first_name', search, True),
                query.Regex('last_name', search, True),
            ]))

        return q

    @staticmethod
    def _format_option_text(user: auth.AbstractUser) -> str:
        r = user.first_last_name

        if auth.get_current_user().is_admin:
            r += ' ({})'.format(user.login)

        return r

    def exec(self):
        c_user = auth.get_current_user()
        if c_user.is_anonymous:
            raise self.forbidden()

        skip = self.arg('skip', 0)

        limit = self.arg('limit', 10)
        if limit > 100:
            limit = 100

        f = auth.find_users(self._get_query(), [('first_name', 1)], limit, skip)

        return {
            'results': [{'id': u.uid, 'text': self._format_option_text(u)} for u in f]
        }
