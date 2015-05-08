import unicodecsv

from django.db import transaction

from wagtail.wagtailredirects import models


class InvalidRedirectCSVException(Exception):
    pass


def import_redirect_csv(f):
    print(f.read())
