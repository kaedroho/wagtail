.. _streamfield:

Freeform page content using StreamField
=======================================

StreamField provides a content editing model suitable for pages that do not follow a fixed structure - such as blog posts or news stories, where the text may be interspersed with subheadings, images, pull quotes and video, and perhaps more specialised content types such as maps and charts (or, for a programming blog, code snippets). In this model, these different content types are represented as a sequence of 'blocks', which can be repeated and arranged in any order.

For further background on StreamField, and why you would use it instead of a rich text field for the article body, see the blog post `Rich text fields and faster horses <https://torchbox.com/blog/rich-text-fields-and-faster-horses/>`__.

StreamField also offers a rich API to define your own block types, ranging from simple collections of sub-blocks (such as a 'person' block consisting of first name, surname and photograph) to completely custom components with their own editing interface. Within the database, the StreamField content is stored as JSON, ensuring that the full informational content of the field is preserved, rather than just an HTML representation of it.


Using StreamField
-----------------

``StreamField`` is a model field that can be defined within your page model like any other field:

.. code-block:: python

    from django.db import models

    from wagtail.wagtailcore.models import Page
    from wagtail.wagtailcore.fields import StreamField
    from wagtail.wagtailcore import blocks
    from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
    from wagtail.wagtailimages.blocks import ImageChooserBlock

    class BlogPage(Page):
        author = models.CharField(max_length=255)
        date = models.DateField("Post date")
        body = StreamField([
            ('heading', blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ('image', ImageChooserBlock()),
        ])

    BlogPage.content_panels = [
        FieldPanel('author'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]


Note: StreamField is not backwards compatible with other field types such as RichTextField; if you migrate an existing field to StreamField, the existing data will be lost.

The parameter to ``StreamField`` is a list of (name, block_type) tuples; 'name' is used to identify the block type within templates and the internal JSON representation (and should follow standard Python conventions for variable names: lower-case and underscores, no spaces) and 'block_type' should be a block definition object as described below. (Alternatively, ``StreamField`` can be passed a single ``StreamBlock`` instance - see :ref:`streamfield_structural_block_types`.)

This defines the set of available block types that can be used within this field. The author of the page is free to use these blocks as many times as desired, in any order.


Basic block types
-----------------

See :doc:`/reference/pages/streamfield_blocks`


.. _streamfield_template_rendering:

Template rendering
------------------

The simplest way to render the contents of a StreamField into your template is to output it as a variable, like any other field:

.. code-block:: django

    {{ self.body }}


This will render each block of the stream in turn, wrapped in a ``<div class="block-my_block_name">`` element (where ``my_block_name`` is the block name given in the StreamField definition). If you wish to provide your own HTML markup, you can instead iterate over the field's value to access each block in turn:

.. code-block:: django

    <article>
        {% for block in self.body %}
            <section>{{ block }}</section>
        {% endfor %}
    </article>


For more control over the rendering of specific block types, each block object provides ``block_type`` and ``value`` properties:

.. code-block:: django

    <article>
        {% for block in self.body %}
            {% if block.block_type == 'heading' %}
                <h1>{{ block.value }}</h1>
            {% else %}
                <section class="block-{{ block.block_type }}">
                    {{ block }}
                </section>
            {% endif %}
        {% endfor %}
    </article>


Each block type provides its own front-end HTML rendering mechanism, and this is used for the output of ``{{ block }}``. For most simple block types, such as CharBlock, this will simply output the field's value, but others will provide their own HTML markup; for example, a ListBlock will output the list of child blocks as a ``<ul>`` element (with each child wrapped in an ``<li>`` element and rendered using the child block's own HTML rendering).

To override this with your own custom HTML rendering, you can pass a ``template`` argument to the block, giving the filename of a template file to be rendered. This is particularly useful for custom block types derived from StructBlock, as the default StructBlock rendering is simple and somewhat generic:

.. code-block:: python

    ('person', blocks.StructBlock(
        [
            ('first_name', blocks.CharBlock(required=True)),
            ('surname', blocks.CharBlock(required=True)),
            ('photo', ImageChooserBlock()),
            ('biography', blocks.RichTextBlock()),
        ],
        template='myapp/blocks/person.html',
        icon='user'
    ))


Or, when defined as a subclass of StructBlock:

.. code-block:: python

    class PersonBlock(blocks.StructBlock):
        first_name = blocks.CharBlock(required=True)
        surname = blocks.CharBlock(required=True)
        photo = ImageChooserBlock()
        biography = blocks.RichTextBlock()

        class Meta:
            template = 'myapp/blocks/person.html'
            icon = 'user'


Within the template, the block value is accessible as the variable ``self``:

.. code-block:: django

    {% load wagtailimages_tags %}

    <div class="person">
        {% image self.photo width-400 %}
        <h2>{{ self.first_name }} {{ self.surname }}</h2>
        {{ self.bound_blocks.biography.render }}
    </div>


The line ``self.bound_blocks.biography.render`` warrants further explanation. While blocks such as RichTextBlock are aware of their own rendering, the actual block *values* (as returned when accessing properties of a StructBlock, such as ``self.biography``), are just plain Python values such as strings. To access the block's proper HTML rendering, you must retrieve the 'bound block' - an object which has access to both the rendering method and the value - via the ``bound_blocks`` property.


Custom block types
------------------

If you need to implement a custom UI, or handle a datatype that is not provided by Wagtail's built-in block types (and cannot built up as a structure of existing fields), it is possible to define your own custom block types. For further guidance, refer to the source code of Wagtail's built-in block classes.

For block types that simply wrap an existing Django form field, Wagtail provides an abstract class ``wagtail.wagtailcore.blocks.FieldBlock`` as a helper. Subclasses just need to set a ``field`` property that returns the form field object:

.. code-block:: python

    class IPAddressBlock(FieldBlock):
        def __init__(self, required=True, help_text=None, **kwargs):
            self.field = forms.GenericIPAddressField(required=required, help_text=help_text)
            super(IPAddressBlock, self).__init__(**kwargs)


Migrations
----------

As with any model field in Django, any changes to a model definition that affect a StreamField will result in a migration file that contains a 'frozen' copy of that field definition. Since a StreamField definition is more complex than a typical model field, there is an increased likelihood of definitions from your project being imported into the migration - which would cause problems later on if those definitions are moved or deleted.

To mitigate this, StructBlock, StreamBlock and ChoiceBlock implement additional logic to ensure that any subclasses of these blocks are deconstructed to plain instances of StructBlock, StreamBlock and ChoiceBlock - in this way, the migrations avoid having any references to your custom class definitions. This is possible because these block types provide a standard pattern for inheritance, and know how to reconstruct the block definition for any subclass that follows that pattern.

If you subclass any other block class, such as ``FieldBlock``, you will need to either keep that class definition in place for the lifetime of your project, or implement a `custom deconstruct method <https://docs.djangoproject.com/en/1.7/topics/migrations/#custom-deconstruct-method>`__ that expresses your block entirely in terms of classes that are guaranteed to remain in place. Similarly, if you customise a StructBlock, StreamBlock or ChoiceBlock subclass to the point where it can no longer be expressed as an instance of the basic block type - for example, if you add extra arguments to the constructor - you will need to provide your own ``deconstruct`` method.
