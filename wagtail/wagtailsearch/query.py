class Query(object):
    def __and__(self, other):
        return ConjunctionQuery([self, other])

    def __or__(self, other):
        return DisjunctionQuery([self, other])

    def __invert__(self):
        return FilterQuery(MatchAllQuery(), exclude=self)


class MatchQuery(Query):
    def __init__(self, query_string, fields=None, operator='or'):
        self.query_string = query_string
        self.fields = fields
        self.operator = operator


class TermQuery(Query):
    def __init__(self, field, value):
        self.field = field
        self.value = value


class PrefixQuery(Query):
    def __init__(self, field, prefix):
        self.field = field
        self.prefix = prefix


class RangeQuery(Query):
    def __init__(self, field, from_=None, from_included=True, to=None, to_included=False):
        self.field = field
        self.from_ = from_
        self.from_included = from_included
        self.to_included = to_included
        self.to = to


class MatchAllQuery(Query):
    """
    A query that matches everything
    """
    pass


class MatchNoneQuery(Query):
    """
    A query that matches nothing
    """
    pass


class ConjunctionQuery(Query):
    """
    Combines multiple queries so that only results that match all sub queries
    are returned
    """
    def __init__(self, subqueries):
        self.subqueries = subqueries


class DisjunctionQuery(Query):
    """
    Combines multiple queries so that results that match any of the sub queries
    are returned
    """
    def __init__(self, subqueries):
        self.subqueries = subqueries


class FilterQuery(Query):
    """
    Takes the results from "query", removes any results that do not match
    "include" and removes any results that do match "exclude"
    """
    def __init__(self, query, include=None, exclude=None):
        self.query = query
        self.include = include
        self.exclude = exclude
