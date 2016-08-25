from __future__ import absolute_import, unicode_literals

import string

from django.db.models.lookups import Lookup
from django.db.models.query import QuerySet
from django.db.models.sql.where import SubqueryConstraint, WhereNode
from django.utils.six import text_type

from wagtail.wagtailsearch.index import class_is_indexed

from . import query

MAX_QUERY_STRING_LENGTH = 255


def normalise_query_string(query_string):
    # Truncate query string
    if len(query_string) > MAX_QUERY_STRING_LENGTH:
        query_string = query_string[:MAX_QUERY_STRING_LENGTH]
    # Convert query_string to lowercase
    query_string = query_string.lower()

    # Strip punctuation characters
    query_string = ''.join([c for c in query_string if c not in string.punctuation])

    # Remove double spaces
    query_string = ' '.join(query_string.split())

    return query_string


class FieldError(Exception):
    pass


def convert_where_node_to_query(where_node):
    def _process_filter(field, lookup, value):
        if lookup == 'exact':
            return query.TermQuery(field, value)

        if lookup == 'isnull':
            if value:
                return query.TermQuery(field, None)
            else:
                return ~query.TermQuery(field, None)

        if lookup == 'startswith':
            return query.PrefixQuery(field, value)

        if lookup == 'gt':
            return query.RangeQuery(field, from_=value, from_included=False)

        if lookup == 'gte':
            return query.RangeQuery(field, from_=value, from_included=True)

        if lookup == 'lt':
            return query.RangeQuery(field, to=value, to_included=False)

        if lookup == 'lte':
            return query.RangeQuery(field, to=value, to_included=True)

        if lookup == 'range':
            lower, upper = value
            return query.RangeQuery(field, from_=lower, from_included=True, to=upper, to_included=True)

        if lookup == 'in':
            return query.DisjunctionQuery([
                query.TermQuery(field, term)
                for term in value
            ])

        raise FilterError(
            'Could not apply filter on search results: "' + field + '__' +
            lookup + ' = ' + text_type(value) + '". Lookup "' + lookup + '"" not recognised.'
        )

    def _connect_filters(filters, connector, negated):
        if filters:
            if len(filters) == 1:
                filter_out = filters[0]
            elif connector.lower() == 'or':
                filter_out = query.DisjunctionQuery([fil for fil in filters if fil is not None])
            elif connector.lower() == 'and':
                filter_out = query.ConjunctionQuery([fil for fil in filters if fil is not None])

            if negated:
                filter_out = ~filter_out

            return filter_out

    # Check if this is a leaf node
    if isinstance(where_node, Lookup):
        field_attname = where_node.lhs.target.attname
        lookup = where_node.lookup_name
        value = where_node.rhs

        # Ignore pointer fields that show up in specific page type queries
        if field_attname.endswith('_ptr_id'):
            return

        # Process the filter
        return _process_filter(field_attname, lookup, value)

    elif isinstance(where_node, SubqueryConstraint):
        raise FilterError('Could not apply filter on search results: Subqueries are not allowed.')

    elif isinstance(where_node, WhereNode):
        # Get child filters
        connector = where_node.connector
        child_filters = [convert_where_node_to_query(child) for child in where_node.children]
        child_filters = [child_filter for child_filter in child_filters if child_filter]

        return _connect_filters(child_filters, connector, where_node.negated)

    else:
        raise FilterError('Could not apply filter on search results: Unknown where node: ' + str(type(where_node)))
