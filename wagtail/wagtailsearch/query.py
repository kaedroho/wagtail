class Query(object):
    def __and__(self, other):
        return ConjunctionQuery([self, other])

    def __or__(self, other):
        return DisjunctionQuery([self, other])

    def __invert__(self):
        return FilterQuery(MatchAllQuery(), exclude=self)

    def rewrite(self):
        return self


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

    def rewrite(self):
        subqueries = []

        for subquery in self.subqueries:
            subquery = subquery.rewrite()

            if isinstance(subquery, MatchNoneQuery):
                # No way this query can match if it contains a MatchNone
                return MatchNoneQuery()
            elif isinstance(subquery, MatchAllQuery):
                # MatchAll has no effect on ConjunctionQuery
                continue
            elif isinstance(subquery, ConjunctionQuery):
                # Flatten nested ConjunctionQueries
                subqueries.extend(subquery.subqueries)
            else:
                subqueries.append(subquery)

        if len(subqueries) == 0:
            # Query must've been entirely made up of MatchAllQueries
            return MatchAllQuery()
        elif len(subqueries) == 1:
            # No need for a ConjunctionQuery anymore
            return subqueries[0]
        else:
            return ConjunctionQuery(subqueries)


class DisjunctionQuery(Query):
    """
    Combines multiple queries so that results that match any of the sub queries
    are returned
    """
    def __init__(self, subqueries):
        self.subqueries = subqueries

    def rewrite(self):
        subqueries = []

        for subquery in self.subqueries:
            subquery = subquery.rewrite()

            if isinstance(subquery, MatchAllQuery):
                # This query will match everything
                return MatchAllQuery()
            elif isinstance(subquery, MatchNoneQuery):
                # MatchNone has no effect on DisjunctionQuery
                continue
            elif isinstance(subquery, DisjunctionQuery):
                # Flatten nested DisjunctionQueries
                subqueries.extend(subquery.subqueries)
            else:
                subqueries.append(subquery)

        if len(subqueries) == 0:
            # Query must've been entirely made up of MatchNoneQueries
            return MatchNoneQuery()
        elif len(subqueries) == 1:
            # No need for a DisjunctionQuery anymore
            return subqueries[0]
        else:
            return DisjunctionQuery(subqueries)


class FilterQuery(Query):
    """
    Takes the results from "query", removes any results that do not match
    "include" and removes any results that do match "exclude"
    """
    def __init__(self, query, include=None, exclude=None):
        self.query = query
        self.include = include
        self.exclude = exclude

    def rewrite(self):
        query = self.query.rewrite()
        include = self.include.rewrite() if self.include else None
        exclude = self.exclude.rewrite() if self.exclude else None

        if isinstance(query, MatchNoneQuery):
            return MatchNoneQuery()

        if isinstance(include, MatchNoneQuery):
            return MatchNoneQuery()

        if isinstance(exclude, MatchAllQuery):
            return MatchNoneQuery()

        if isinstance(include, MatchAllQuery):
            include = None

        if isinstance(exclude, MatchNoneQuery):
            exclude = None

        if include is None and exclude is None:
            return query

        return FilterQuery(query, include=include, exclude=exclude)
