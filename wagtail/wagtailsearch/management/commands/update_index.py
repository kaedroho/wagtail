from __future__ import absolute_import, unicode_literals

import collections

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.wagtailsearch.backends import get_search_backend
from wagtail.wagtailsearch.index import get_indexed_models


def get_model_root(model):
    if model._meta.parents:
        return list(model._meta.parents.items())[0][0]
    else:
        return model


def group_models_by_root(models):
    grouped_models = collections.OrderedDict()

    for model in models:
        root = get_model_root(model)
        grouped_models.setdefault(root, [])
        grouped_models[root].append(model)

    return grouped_models


class Command(BaseCommand):
    def update_backend(self, backend_name, schema_only=False):
        # Print info
        self.stdout.write("Updating backend: " + backend_name)

        # Get backend
        backend = get_search_backend(backend_name)

        for root_model, models in group_models_by_root(get_indexed_models()).items():
            self.stdout.write(backend_name + ": Rebuilding index for %s" % root_model._meta.verbose_name_plural)

            rebuilder = backend.get_rebuilder(backend.get_index_for_model(root_model))
            index = rebuilder.start()

            #self.stdout.write(backend_name + ": Writing schema")
            for model in models:
                index.add_model(model)

            # Index objects
            #self.stdout.write(backend_name + ": Writing objects")
            object_count = 0
            if not schema_only:
                for model in models:
                    # Add items (1000 at a time)
                    for chunk in self.print_iter_progress(self.queryset_chunks(model.get_indexed_objects())):
                        index.add_items(model, chunk)
                        object_count += len(chunk)

            rebuilder.finish()

            self.print_newline()
            self.stdout.write(backend_name + ": (indexed %d objects)" % object_count)
            self.print_newline()
            self.print_newline()

        return

        # Get rebuilder
        rebuilder = backend.get_rebuilder()

        if not rebuilder:
            self.stdout.write(backend_name + ": Backend doesn't require rebuild. Skipping")
            return

        # Start rebuild
        self.stdout.write(backend_name + ": Starting rebuild")
        index = rebuilder.start()

        for model in get_indexed_models():
            self.stdout.write(backend_name + ": Indexing model '%s.%s'" % (
                model._meta.app_label,
                model.__name__,
            ))

            # Add model
            index.add_model(model)

            # Index objects
            object_count = 0
            if not schema_only:
                # Add items (1000 at a time)
                for chunk in self.print_iter_progress(self.queryset_chunks(model.get_indexed_objects())):
                    index.add_items(model, chunk)
                    object_count += len(chunk)

            self.stdout.write("(indexed %d objects)" % object_count)
            self.print_newline()

        # Finish rebuild
        self.stdout.write(backend_name + ": Finishing rebuild")
        rebuilder.finish()

    def add_arguments(self, parser):
        parser.add_argument(
            '--backend', action='store', dest='backend_name', default=None,
            help="Specify a backend to update")
        parser.add_argument(
            '--schema-only', action='store', dest='schema_only', default=None,
            help="Prevents loading any data into the index")

    def handle(self, **options):
        # Get list of backends to index
        if options['backend_name']:
            # index only the passed backend
            backend_names = [options['backend_name']]
        elif hasattr(settings, 'WAGTAILSEARCH_BACKENDS'):
            # index all backends listed in settings
            backend_names = settings.WAGTAILSEARCH_BACKENDS.keys()
        else:
            # index the 'default' backend only
            backend_names = ['default']

        # Update backends
        for backend_name in backend_names:
            self.update_backend(backend_name, schema_only=options['schema_only'])

    def print_newline(self):
        self.stdout.write('')

    def print_iter_progress(self, iterable):
        """
        Print a progress meter while iterating over an iterable. Use it as part
        of a ``for`` loop::

            for item in self.print_iter_progress(big_long_list):
                self.do_expensive_computation(item)

        A ``.`` character is printed for every value in the iterable,
        a space every 10 items, and a new line every 50 items.
        """
        for i, value in enumerate(iterable, start=1):
            yield value
            self.stdout.write('.', ending='')
            if i % 50 == 0:
                self.print_newline()

            elif i % 10 == 0:
                self.stdout.write(' ', ending='')

            self.stdout.flush()

    # Atomic so the count of models doesnt change as it is iterated
    @transaction.atomic
    def queryset_chunks(self, qs, chunk_size=1000):
        """
        Yield a queryset in chunks of at most ``chunk_size``. The chunk yielded
        will be a list, not a queryset. Iterating over the chunks is done in a
        transaction so that the order and count of items in the queryset
        remains stable.
        """
        i = 0
        while True:
            items = list(qs[i * chunk_size:][:chunk_size])
            if not items:
                break
            yield items
            i += 1
