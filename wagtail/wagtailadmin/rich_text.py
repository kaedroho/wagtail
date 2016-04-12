from __future__ import absolute_import, unicode_literals

import json

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms import Media, widgets
from django.utils.module_loading import import_string

from wagtail.utils.widgets import WidgetWithScript
from wagtail.wagtailadmin.edit_handlers import RichTextFieldPanel
from wagtail.wagtailcore.rich_text import DbWhitelister, expand_db_html


class HalloRichTextArea(WidgetWithScript, widgets.Textarea):
    def __init__(self, plugins=None, plugin_settings=None, **kwargs):
        # plugins is an ordered list of plugins to display in this widget
        # plugin_settings is a dictionary of plugin name to configuration. This
        # allows overriding the default configuration of specific plugins
        self.plugins = plugins
        self.plugin_settings = plugin_settings
        super(HalloRichTextArea, self).__init__(**kwargs)

    def get_panel(self):
        return RichTextFieldPanel

    def render(self, name, value, attrs=None):
        if value is None:
            translated_value = None
        else:
            translated_value = expand_db_html(value, for_editor=True)
        return super(HalloRichTextArea, self).render(name, translated_value, attrs)

    def render_js_init(self, id_, name, value):
        return "makeHalloRichTextEditable({0}, {1}, {2});".format(json.dumps(id_), json.dumps(self.plugins), json.dumps(self.plugin_settings))

    def value_from_datadict(self, data, files, name):
        original_value = super(HalloRichTextArea, self).value_from_datadict(data, files, name)
        if original_value is None:
            return None
        return DbWhitelister.clean(original_value)

    @property
    def media(self):
        return Media(js=[
            static('wagtailadmin/js/vendor/hallo.js'),
            static('wagtailadmin/js/hallo-bootstrap.js'),
            static('wagtailadmin/js/hallo-plugins/hallo-wagtaillink.js'),
            static('wagtailadmin/js/hallo-plugins/hallo-hr.js'),
            static('wagtailadmin/js/hallo-plugins/hallo-requireparagraphs.js'),
        ])


DEFAULT_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.wagtailadmin.rich_text.HalloRichTextArea'
    }
}


def get_rich_text_editor(name='default'):
    editor_settings = getattr(settings, 'WAGTAILADMIN_RICH_TEXT_EDITORS', DEFAULT_RICH_TEXT_EDITORS)

    editor = editor_settings[name]
    kwargs = editor.get('OPTIONS', {})
    return import_string(editor['WIDGET'])(**kwargs)
