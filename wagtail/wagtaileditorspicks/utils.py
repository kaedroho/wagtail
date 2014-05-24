import string


def normalise_query_string(query_string):
    """
    This function converts a query string into a standard format so
    they can be easily compared.
    """
    # Convert query_string to lowercase
    query_string = query_string.lower()

    # Strip punctuation characters
    query_string = ''.join([c for c in query_string if c not in string.punctuation])

    # Replace multi spaces with single space and completely
    # remove leading and trailing spaces
    query_string = ' '.join(query_string.split())

    return query_string
