"""PytSite Authentication Settings Plugin Forms
"""
from pytsite import lang as _lang
from plugins import widget as _widget, auth_ui as _auth_ui, settings as _settings

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Form(_settings.Form):
    """PytSite Auth Settings Form
    """

    def _on_setup_widgets(self):
        self.add_widget(_widget.select.Checkbox(
            weight=10,
            uid='setting_signup_enabled',
            label=_lang.t('auth_ui@allow_sign_up'),
        ))

        ui_driver_items = [(driver.name, driver.description) for driver in _auth_ui.get_drivers().values()]

        self.add_widget(_widget.select.Select(
            weight=20,
            uid='setting_ui_driver',
            append_none_item=False,
            label=_lang.t('auth_ui@default_ui_driver'),
            h_size='col-xs-12 col-sm-6 col-md-3',
            items=sorted(ui_driver_items, key=lambda i: i[0]),
            default=_auth_ui.get_driver().name,
        ))

        super()._on_setup_widgets()
