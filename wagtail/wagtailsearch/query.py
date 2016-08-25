class Query(object):
    def __and__(self, other):
        return ConjunctionQuery([self, other])

    def __or__(self, other):
        return DisjunctionQuery([self, other])

    def __invert__(self):
        return FilterQuery(MatchAllQuery(), exclude=self)


class MatchQuery(Query):
    def __init__(self, query_string, fields=None, operator=None):
        self.query_string = query_string
        self.fields = fields
        self.operator = operator or 'or'

    def __repr__(self):
        return '<Match [{}]: "{}" {}>'.format(
            ','.join(self.fields) if self.fields else ['all'],
            self.query_string,
            self.operator,
        )


class TermQuery(Query):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __repr__(self):
        return '<Term {}: "{}">'.format(self.field, self.value)


class PrefixQuery(Query):
    def __init__(self, field, prefix):
        self.field = field
        self.prefix = prefix

    def __repr__(self):
        return '<Prefix {}: "{}">'.format(self.field, self.prefix)


class RangeQuery(Query):
    def __init__(self, field, from_=None, from_included=True, to=None, to_included=False):
        self.field = field
        self.from_ = from_
        self.from_included = from_included
        self.to_included = to_included
        self.to = to

    def __repr__(self):
        return '<Range {}...{}>'.format(self.from_, self.to)


class MatchAllQuery(Query):
    """
    A query that matches everything
    """
    def __repr__(self):
        return '<All>'


class MatchNoneQuery(Query):
    """
    A query that matches nothing
    """
    def __repr__(self):
        return '<None>'


class ConjunctionQuery(Query):
    """
    Combines multiple queries so that only results that match all sub queries
    are returned
    """
    def __init__(self, subqueries):
        self.subqueries = subqueries

    def __repr__(self):
        return '<Conjunction [{}]>'.format(','.join([repr(query) for query in self.subqueries]))


class DisjunctionQuery(Query):
    """
    Combines multiple queries so that results that match any of the sub queries
    are returned
    """
    def __init__(self, subqueries):
        self.subqueries = subqueries

    def __repr__(self):
        return '<Disjunction [{}]>'.format(','.join([repr(query) for query in self.subqueries]))


class FilterQuery(Query):
    """
    Takes the results from "query", removes any results that do not match
    "include" and removes any results that do match "exclude"
    """
    def __init__(self, query, include=None, exclude=None):
        self.query = query
        self.include = include
        self.exclude = exclude

    def __repr__(self):
        return '<Filter {} include={} exclude={}>'.format(repr(self.query), repr(self.include), repr(self.exclude))
