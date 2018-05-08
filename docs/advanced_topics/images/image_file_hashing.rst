Image file hashing
==================

Wagtail automatically generates SHA-1 hashes for images files and stores them in
the ``file_hash`` field on the image model. The value of this field should be
exactly the same as the result of a ``shasum`` call on the image file.

This isn't currently used by Wagtail itself, but it may be used by a developer for
quickly checking if an image is already in use on the site or has been duplicated.
Wagtail may use it in rendition filenames in the future to allow images to be served
over a CDN without requiring automatic invalidation.

Generating hashes for images manually
-------------------------------------

There's a couple of cases where you might want to trigger Wagtail to generate hashes:

 - You have just updated Wagtail to version [INSERT VERSION HERE], when this feature was added
 - You upload images through a separate interface to Wagtail's admin (such as: S3 direct upload or a content importer)

From the shell
~~~~~~~~~~~~~~

Run the following in the shell:

.. code-block:: bash

    ./manage.py calculate_image_hashes

This will find images that do not currently have the ``file_hash`` field set and for each one, it will
open the image file and generate a hash.

.. note::

    This will not detect when an existing image has been updated. If you do this programmatically,
    set the ``file_hash`` field to a blank string then the management command will regenerate it.

From Python
~~~~~~~~~~~

If you're writing a view/content importer in Python, you can add the following code
to your save function to generate the hash:

.. code-block:: python

    import hashlib

    # 'contents' should be a bytestring containing the contents of the file
    image.file_hash = hashlib.sha1(contents).hexdigest()
