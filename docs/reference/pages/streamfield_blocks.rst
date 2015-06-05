StreamField Block Types Reference
=================================

.. automodule:: wagtail.wagtailcore.blocks


All block types accept the following optional keyword arguments:

``default``
  The default value that a new 'empty' block should receive.

``label``
  The label to display in the editor interface when referring to this block - defaults to a prettified version of the block name (or, in a context where no name is assigned - such as within a ``ListBlock`` - the empty string).

``icon``
  The name of the icon to display for this block type in the menu of available block types. For a list of icon names, see the Wagtail style guide, which can be enabled by adding ``wagtail.contrib.wagtailstyleguide`` to your project's ``INSTALLED_APPS``.

``template``
  The path to a Django template that will be used to render this block on the front end. See :ref:`streamfield_template_rendering`.

The basic block types provided by Wagtail are as follows:

CharBlock
~~~~~~~~~

``wagtail.wagtailcore.blocks.CharBlock``

A single-line text input. The following keyword arguments are accepted:

``required`` (default: True)
  If true, the field cannot be left blank.

``max_length``, ``min_length``
  Ensures that the string is at most or at least the given length.

``help_text``
  Help text to display alongside the field.

TextBlock
~~~~~~~~~

``wagtail.wagtailcore.blocks.TextBlock``

A multi-line text input. As with ``CharBlock``, the keyword arguments ``required``, ``max_length``, ``min_length`` and ``help_text`` are accepted.

URLBlock
~~~~~~~~

``wagtail.wagtailcore.blocks.URLBlock``

A single-line text input that validates that the string is a valid URL. The keyword arguments ``required``, ``max_length``, ``min_length`` and ``help_text`` are accepted.

BooleanBlock
~~~~~~~~~~~~

``wagtail.wagtailcore.blocks.BooleanBlock``

A checkbox. The keyword arguments ``required`` and ``help_text`` are accepted. As with Django's ``BooleanField``, a value of ``required=True`` (the default) indicates that the checkbox must be ticked in order to proceed; for a checkbox that can be ticked or unticked, you must explicitly pass in ``required=False``.

DateBlock
~~~~~~~~~

``wagtail.wagtailcore.blocks.DateBlock``

A date picker. The keyword arguments ``required`` and ``help_text`` are accepted.

TimeBlock
~~~~~~~~~

``wagtail.wagtailcore.blocks.TimeBlock``

A time picker. The keyword arguments ``required`` and ``help_text`` are accepted.

DateTimeBlock
~~~~~~~~~~~~~

``wagtail.wagtailcore.blocks.DateTimeBlock``

A combined date / time picker. The keyword arguments ``required`` and ``help_text`` are accepted.

RichTextBlock
~~~~~~~~~~~~~

``wagtail.wagtailcore.blocks.RichTextBlock``

A WYSIWYG editor for creating formatted text including links, bold / italics etc.

RawHTMLBlock
~~~~~~~~~~~~

``wagtail.wagtailcore.blocks.RawHTMLBlock``

A text area for entering raw HTML which will be rendered unescaped in the page output. The keyword arguments ``required``, ``max_length``, ``min_length`` and ``help_text`` are accepted.

.. WARNING::
   When this block is in use, there is nothing to prevent editors from inserting malicious scripts into the page, including scripts that would allow the editor to acquire administrator privileges when another administrator views the page. Do not use this block unless your editors are fully trusted.

ChoiceBlock
~~~~~~~~~~~

``wagtail.wagtailcore.blocks.ChoiceBlock``

A dropdown select box for choosing from a list of choices. The following keyword arguments are accepted:

``choices``
  A list of choices, in any format accepted by Django's ``choices`` parameter for model fields: https://docs.djangoproject.com/en/stable/ref/models/fields/#field-choices

``required`` (default: True)
  If true, the field cannot be left blank.

``help_text``
  Help text to display alongside the field.

``ChoiceBlock`` can also be subclassed to produce a reusable block with the same list of choices everywhere it is used. For example, a block definition such as:

.. code-block:: python

    blocks.ChoiceBlock(choices=[
        ('tea', 'Tea'),
        ('coffee', 'Coffee'),
    ], icon='cup')


could be rewritten as a subclass of ChoiceBlock:

.. code-block:: python

    class DrinksChoiceBlock(blocks.ChoiceBlock):
        choices = [
            ('tea', 'Tea'),
            ('coffee', 'Coffee'),
        ]

        class Meta:
            icon = 'cup'


``StreamField`` definitions can then refer to ``DrinksChoiceBlock()`` in place of the full ``ChoiceBlock`` definition.

PageChooserBlock
~~~~~~~~~~~~~~~~

``wagtail.wagtailcore.blocks.PageChooserBlock``

A control for selecting a page object, using Wagtail's page browser. The keyword argument ``required`` is accepted.

DocumentChooserBlock
~~~~~~~~~~~~~~~~~~~~

``wagtail.wagtaildocs.blocks.DocumentChooserBlock``

A control to allow the editor to select an existing document object, or upload a new one. The keyword argument ``required`` is accepted.

ImageChooserBlock
~~~~~~~~~~~~~~~~~

``wagtail.wagtailimages.blocks.ImageChooserBlock``

A control to allow the editor to select an existing image, or upload a new one. The keyword argument ``required`` is accepted.

SnippetChooserBlock
~~~~~~~~~~~~~~~~~~~

``wagtail.wagtailsnippets.blocks.SnippetChooserBlock``

A control to allow the editor to select a snippet object. Requires one positional argument: the snippet class to choose from. The keyword argument ``required`` is accepted.

EmbedBlock
~~~~~~~~~~

``wagtail.wagtailembeds.blocks.EmbedBlock``

A field for the editor to enter a URL to a media item (such as a YouTube video) to appear as embedded media on the page. The keyword arguments ``required``, ``max_length``, ``min_length`` and ``help_text`` are accepted.


.. _streamfield_structural_block_types:

Structural block types
----------------------

In addition to the basic block types above, it is possible to define new block types made up of sub-blocks: for example, a 'person' block consisting of sub-blocks for first name, surname and image, or a 'carousel' block consisting of an unlimited number of image blocks. These structures can be nested to any depth, making it possible to have a structure containing a list, or a list of structures.

StructBlock
~~~~~~~~~~~

``wagtail.wagtailcore.blocks.StructBlock``

A block consisting of a fixed group of sub-blocks to be displayed together. Takes a list of (name, block_definition) tuples as its first argument:

.. code-block:: python

    ('person', blocks.StructBlock([
        ('first_name', blocks.CharBlock(required=True)),
        ('surname', blocks.CharBlock(required=True)),
        ('photo', ImageChooserBlock()),
        ('biography', blocks.RichTextBlock()),
    ], icon='user'))


Alternatively, the list of sub-blocks can be provided in a subclass of StructBlock:

.. code-block:: python

    class PersonBlock(blocks.StructBlock):
        first_name = blocks.CharBlock(required=True)
        surname = blocks.CharBlock(required=True)
        photo = ImageChooserBlock()
        biography = blocks.RichTextBlock()

        class Meta:
            icon = 'user'


The ``Meta`` class supports the properties ``default``, ``label``, ``icon`` and ``template``; these have the same meanings as when they are passed to the block's constructor.

This defines ``PersonBlock()`` as a block type that can be re-used as many times as you like within your model definitions:

.. code-block:: python

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('person', PersonBlock()),
    ])


ListBlock
~~~~~~~~~

``wagtail.wagtailcore.blocks.ListBlock``

A block consisting of many sub-blocks, all of the same type. The editor can add an unlimited number of sub-blocks, and re-order and delete them. Takes the definition of the sub-block as its first argument:

.. code-block:: python

    ('ingredients_list', blocks.ListBlock(blocks.CharBlock(label="Ingredient")))


Any block type is valid as the sub-block type, including structural types:

.. code-block:: python

    ('ingredients_list', blocks.ListBlock(blocks.StructBlock([
        ('ingredient', blocks.CharBlock(required=True)),
        ('amount', blocks.CharBlock()),
    ])))


StreamBlock
~~~~~~~~~~~

``wagtail.wagtailcore.blocks.StreamBlock``

A block consisting of a sequence of sub-blocks of different types, which can be mixed and reordered in any order. Used as the overall mechanism of the StreamField itself, but can also be nested or used within other structural block types. Takes a list of (name, block_definition) tuples as its first argument:

.. code-block:: python

    ('carousel', blocks.StreamBlock(
        [
            ('image', ImageChooserBlock()),
            ('quotation', blocks.StructBlock([
                ('text', blocks.TextBlock()),
                ('author', blocks.CharBlock()),
            ])),
            ('video', EmbedBlock()),
        ],
        icon='cogs'
    ))


As with StructBlock, the list of sub-blocks can also be provided as a subclass of StreamBlock:

.. code-block:: python

    class CarouselBlock(blocks.StreamBlock):
        image = ImageChooserBlock()
        quotation = blocks.StructBlock([
            ('text', blocks.TextBlock()),
            ('author', blocks.CharBlock()),
        ])
        video = EmbedBlock()

        class Meta:
            icon='cogs'


Since ``StreamField`` accepts an instance of ``StreamBlock`` as a parameter, in place of a list of block types, this makes it possible to re-use a common set block types without repeating definitions:

.. code-block:: python

    class HomePage(Page):
        carousel = StreamField(CarouselBlock())
