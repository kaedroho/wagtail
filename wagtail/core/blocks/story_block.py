from wagtail.core.telepath import register

from .struct_block import StructBlock
from .field_block import IntegerBlock, SingleLineRichTextBlock, CharBlock, PageChooserBlock
from .stream_block import StreamBlock, StreamBlockAdapter
from .list_block import ListBlock


class HeadingBlock(StructBlock):
    content = SingleLineRichTextBlock(allow_newlines=False)
    level = IntegerBlock()
    id = CharBlock()


class ParagraphBlock(StructBlock):
    content = SingleLineRichTextBlock()


class ListItemBlock(StructBlock):
    content = SingleLineRichTextBlock()
    depth = IntegerBlock()


class StoryBlock(StreamBlock):
    heading = HeadingBlock()
    paragraph = ParagraphBlock()
    ordered_list_item = ListItemBlock()
    unordered_list_item = ListItemBlock()


class StoryBlockAdapter(StreamBlockAdapter):
    js_constructor = 'wagtail.blocks.StoryBlock'


register(StoryBlockAdapter(), StoryBlock)


block_classes = [
    HeadingBlock, ParagraphBlock, StoryBlock
]
DECONSTRUCT_ALIASES = {
    cls: 'wagtail.core.blocks.%s' % cls.__name__
    for cls in block_classes
}
__all__ = [cls.__name__ for cls in block_classes]
