import unicodecsv

from django.db import transaction

from wagtail.wagtailredirects import models


class InvalidRedirectCSVException(Exception):
    pass


def import_redirect_csv(f):
    try:
        reader = unicodecsv.reader(f.read().decode('UTF-8').splitlines())
    except UnicodeDecodeError:
        raise InvalidRedirectCSVException("Unable to read file. Is it a valid CSV file with UTF-8 encoding?")

    for row in reader:
        # Check number of columns
        if len(row) != 2:
            raise InvalidRedirectCSVException("CSV file has %d columns. It should have 2." % len(row))

        # Skip row if all fields are blank
        if not any(row):
            continue

        # Get from_path and to_url fields
        from_path = row[0].strip()
        to_url = row[1].strip()

        # Both fields are required
        if not from_path:
            raise InvalidRedirectCSVException("[ROW %d] From path must not be blank." % reader.line_num)

        if not to_url:
            raise InvalidRedirectCSVException("[ROW %d] URL must not be blank." % reader.line_num)

        # from_path must start with a /
        if not from_path.startswith('/'):
            raise InvalidRedirectCSVException("[ROW %d] From path must begin with a '/'." % reader.line_num)

        # To URL must either be an internal link or a valid URL
        to_url_is_external = not to_url.startswith('/')

        if to_url_is_external:
            pass # CHECK URL IS VALID
