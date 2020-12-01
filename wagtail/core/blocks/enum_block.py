import collections

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from wagtail.admin.staticfiles import versioned_static
from wagtail.core.utils import escape_script

from .base import Block, DeclarativeSubBlocksMetaclass
from .utils import js_dict


__all__ = ['BaseEnumBlock', 'EnumBlock', 'EnumValue']


class EnumValue:
    """ A class that generates a EnumBlock value from provided sub-blocks """
    def __init__(self, block, type, value):
        self.block = block
        self.type = type
        self.value = value

    def __html__(self):
        return self.block.render(self)

    def render_as_block(self, context=None):
        return self.block.render(self, context=context)

    @cached_property
    def bound_block(self):
        return self.block.child_blocks[self.type].bind(self.value)


class BaseEnumBlock(Block):

    def __init__(self, local_blocks=None, **kwargs):
        self._constructor_kwargs = kwargs

        super().__init__(**kwargs)

        # create a local (shallow) copy of base_blocks so that it can be supplemented by local_blocks
        self.child_blocks = self.base_blocks.copy()
        if local_blocks:
            for name, block in local_blocks:
                block.set_name(name)
                self.child_blocks[name] = block

        self.child_js_initializers = {}
        for name, block in self.child_blocks.items():
            js_initializer = block.js_initializer()
            if js_initializer is not None:
                self.child_js_initializers[name] = js_initializer

        self.dependencies = self.child_blocks.values()

        self.type_field = forms.CharField(
            required=True,
            widget=forms.HiddenInput,
        )

    def get_default(self):
        """
        Any default value passed in the constructor or self.meta is going to be a dict
        rather than a EnumValue; for consistency, we need to convert it to a EnumValue
        for EnumBlock to work with
        """
        return self._to_enum_value(*self.meta.default) if self.meta.default else None

    def render_internal(self, block_type_name, value, prefix, index, errors=None, id=None):
        """
        Render the HTML for a single list item. This consists of a container, hidden fields
        to manage ID/deleted state/type, delete/reorder buttons, and the child block's own HTML.
        """
        child_block = self.child_blocks[block_type_name]
        child = child_block.bind(value, prefix="%s-value" % prefix, errors=errors)
        return render_to_string('wagtailadmin/block_forms/enum_internal.html', {
            'block_type_name': block_type_name,
            'child_block': child_block,
            'prefix': prefix,
            'child': child,
            'index': index,
            'block_id': id,
        })

    def html_declarations(self):
        return format_html_join(
            '\n', '<script type="text/template" id="{0}-newmember-{1}">{2}</script>',
            [
                (
                    self.definition_prefix,
                    name,
                    mark_safe(escape_script(self.render_internal(name, child_block.get_default(), '__PREFIX__', '')))
                )
                for name, child_block in self.child_blocks.items()
            ]
        )

    def js_initializer(self):
        # skip JS setup entirely if no children have js_initializers
        if not self.child_js_initializers:
            return None

        return "EnumBlock(%s)" % js_dict(self.child_js_initializers)

    @property
    def media(self):
        return forms.Media(js=[versioned_static('wagtailadmin/js/blocks/enum.js')])

    def get_form_context(self, value, prefix='', errors=None):
        if errors:
            if len(errors) > 1:
                # We rely on EnumBlock.clean throwing a single ValidationError with a specially crafted
                # 'params' attribute that we can pull apart and distribute to the child blocks
                raise TypeError('EnumBlock.render_form unexpectedly received multiple errors')
            error_dict = errors.as_data()[0].params
        else:
            error_dict = {}

        bound_child_blocks = collections.OrderedDict([
            (
                name,
                block.bind(value.value if value and value.type == name else block.get_default(),
                           prefix="%s-%s" % (prefix, name), errors=error_dict.get(name))
            )
            for name, block in self.child_blocks.items()
        ])

        return {
            'children': bound_child_blocks,
            'help_text': getattr(self.meta, 'help_text', None),
            'classname': self.meta.form_classname,
            'block_definition': self,
            'prefix': prefix,
        }

    def render_form(self, value, prefix='', errors=None):
        context = self.get_form_context(value, prefix=prefix, errors=errors)

        return mark_safe(render_to_string(self.meta.form_template, context))

    def value_from_datadict(self, data, files, prefix):
        block_type = self.type_field.widget.value_from_datadict(data, files, prefix + '-type')
        if not block_type:
            return None

        value = self.child_blocks[block_type].value_from_datadict(data, files, '%s-%s' % (prefix, block_type))
        return self._to_enum_value(block_type, value)

    def value_omitted_from_data(self, data, files, prefix):
        return all(
            block.value_omitted_from_data(data, files, '%s-%s' % (prefix, name))
            for name, block in self.child_blocks.items()
        )

    def clean(self, value):
        # TODO: Required?
        if value is not None:
            if value.type not in self.child_blocks:
                # TODO nicer error
                raise ValidationError("EnumBlock unrecognised type")

            self.child_blocks[value.type].clean(value.value)

        return value

    def to_python(self, value):
        """ Recursively call to_python on children and return as a EnumValue """

        if value is not None:
            block_type = value['type']
            block_value = self.child_blocks[block_type].to_python(value['value'])
            return self._to_enum_value(block_type, block_value)


    def bulk_to_python(self, values):
        return [
            self.to_python(value)
            for value in values
        ]

    def _to_enum_value(self, type, value):
        """ Return a Enumvalue representation of the sub-blocks in this block """
        return self.meta.value_class(self, type, value)

    def get_prep_value(self, value):
        """ Recursively call get_prep_value on children and return as a plain dict """
        if value is not None:
            return {
                'type': value.type,
                'value': self.child_blocks[value.type].get_prep_value(value.value)
            }

    def get_api_representation(self, value, context=None):
        """ Recursively call get_api_representation on children and return as a plain dict """
        if value is not None:
            return {
                'type': value.type,
                'value': self.child_blocks[value.type].get_prep_value(value.value)
            }

    def get_searchable_content(self, value):
        if value is not None:
            return self.child_blocks[value.type].get_searchable_content(value.value)
        else:
            return []

    def deconstruct(self):
        """
        Always deconstruct EnumBlock instances as if they were plain EnumBlocks with all of the
        field definitions passed to the constructor - even if in reality this is a subclass of EnumBlock
        with the fields defined declaratively, or some combination of the two.

        This ensures that the field definitions get frozen into migrations, rather than leaving a reference
        to a custom subclass in the user's models.py that may or may not stick around.
        """
        path = 'wagtail.core.blocks.EnumBlock'
        args = [list(self.child_blocks.items())]
        kwargs = self._constructor_kwargs
        return (path, args, kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        for name, child_block in self.child_blocks.items():
            errors.extend(child_block.check(**kwargs))
            errors.extend(child_block._check_name(**kwargs))

        return errors

    def render_basic(self, value, context=None):
        if value is not None:
            return self.child_blocks[value.type].render_basic(value.value, context=context)
        else:
            return ''

    class Meta:
        default = None
        form_classname = 'enum-block'
        form_template = 'wagtailadmin/block_forms/enum.html'
        value_class = EnumValue
        # No icon specified here, because that depends on the purpose that the
        # block is being used for. Feel encouraged to specify an icon in your
        # descendant block type
        icon = "placeholder"


class EnumBlock(BaseEnumBlock, metaclass=DeclarativeSubBlocksMetaclass):
    pass
