.. _pages-theory:

========
Overview
========

This document aims to give a brief overview of the components of Wagtail.

Pages
~~~~~

Most of the content in a Wagtail site is stored in Pages.


 - All pages are stored in a materialised-path tree structure
 - Each page has a type that is represented by a Django model (eg, Blog page, )
 each page has a type represented by a Django model containing .


https://docs.djangoproject.com/en/1.8/topics/db/models/#multi-table-inheritance


Sites
~~~~~

A Wagtail site can respond on different hostnames, each hostname can have a different root page.


Images
~~~~~~

Renditions and filters, etc


Search
~~~~~~

Full text search. Powered by Elasticsearch


Snippets
~~~~~~~~

Just Django models. Nothing special really.


Documents
~~~~~~~~~

A place to put "Documents". But any file format is allowed


Embeds
~~~~~~

Youtube/vimeo videos, etc. Fetched using oembed and cached locally. Embedly support
