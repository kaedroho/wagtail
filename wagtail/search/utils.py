import operator
import re
from functools import partial, reduce


NOT_SET = object()


def balanced_reduce(operator, seq, initializer=NOT_SET):
    """
    Has the same result as Python's reduce function, but performs the calculations in a different order.

    This is important when the operator is constructing data structures such as search query clases.
    This method will make the resulting data structures flatter, so operations that need to traverse
    them don't end up crashing with recursion errors.

    For example:

    Python's builtin reduce() function will do the following calculation:

    reduce(add, [1, 2, 3, 4, 5, 6, 7, 8])
    (1 + (2 + (3 + (4 + (5 + (6 + (7 + 8)))))))

    When using this with query classes, it would create a large data structure with a depth of 7
    Whereas balanced_reduce will execute this like so:

    balanced_reduce(add, [1, 2, 3, 4, 5, 6, 7, 8])
    ((1 + 2) + (3 + 4)) + ((5 + 6) + (7 + 8))

    Which only has a depth of 2
    """
    # Casting all iterables to list makes the implementation simpler
    if not isinstance(seq, list):
        seq = list(seq)

    # Note, it needs to be possible to use None as an initial value
    if initializer is not NOT_SET:
        if len(seq) == 0:
            return initializer
        else:
            return operator(initializer, balanced_reduce(operator, seq))

    if len(seq) == 0:
        raise TypeError("reduce() of empty sequence with no initial value")
    elif len(seq) == 1:
        return seq[0]
    else:
        break_point = len(seq) // 2
        first_set = balanced_reduce(operator, seq[:break_point])
        second_set = balanced_reduce(operator, seq[break_point:])
        return operator(first_set, second_set)

# Reduce any iterable to a single value using a logical OR e.g. (a | b | ...)
OR = partial(balanced_reduce, operator.or_)
# Reduce any iterable to a single value using a logical AND e.g. (a & b & ...)
AND = partial(balanced_reduce, operator.and_)
# Reduce any iterable to a single value using an addition
ADD = partial(balanced_reduce, operator.add)
# Reduce any iterable to a single value using a multiplication
MUL = partial(balanced_reduce, operator.mul)

MAX_QUERY_STRING_LENGTH = 255


def normalise_query_string(query_string):
    # Truncate query string
    if len(query_string) > MAX_QUERY_STRING_LENGTH:
        query_string = query_string[:MAX_QUERY_STRING_LENGTH]
    # Convert query_string to lowercase
    query_string = query_string.lower()

    # Remove leading, trailing and multiple spaces
    query_string = re.sub(' +', ' ', query_string).strip()

    return query_string


def separate_filters_from_query(query_string):
    filters_regexp = r'(\w+):(\w+|".+")'

    filters = {}
    for match_object in re.finditer(filters_regexp, query_string):
        key, value = match_object.groups()
        filters[key] = value.strip("\"")

    query_string = re.sub(filters_regexp, '', query_string).strip()

    return filters, query_string
