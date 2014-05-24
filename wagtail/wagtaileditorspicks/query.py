from django.db import models
from django.utils import timezone
import datetime

from .utils import normalise_query_string
from .models import QueryDailyHits, EditorsPick


class Query(object):
    def __init__(self, query_string):
        self.query_string = query_string

    def add_hit(self, date=None):
        """
        This adds one to the hit counter for this query
        """
        # Get date
        if date is None:
            date = timezone.now()

        # Get or create todays QueryDailyHits object
        daily_hits, created = QueryDailyHits.objects.get_or_create(
            query_string=self.query_string, date=date)

        # Add a hit atomically
        QueryDailyHits.objects.filter(id=daily_hits.id).update(
            hits=models.F('hits') + 1)

    def get_hits(self, date=None):
        """
        This gets the total number of hits this query has had
        for the past 7 days
        """
        if date is None:
            date = timezone.now()
        date_since = date - datetime.timedelta(days=7)

        # Get daily hits objects
        daily_hits = QueryDailyHits.objects.filter(
            query_string=self.query_string,
            date__gte=date_since, date__lte=date)

        # Sum up the hits and return
        return daily_hits.aggregate(total_hits=models.Sum('hits'))['total_hits'] or 0

    hits = property(get_hits)

    @property
    def editors_picks(self):
        return EditorsPick.objects.filter(query_string=self.query_string)

    @property
    def slug(self):
        return self.query_string.replace(' ', '-')

    @classmethod
    def from_slug(cls, slug):
        query_string = slug.replace('-', ' ')
        return cls(normalise_query_string(query_string))

    @classmethod
    def get_most_popular(self, date=None):
        """
        This returns a ValuesQuerySet of query_strings ordered by popularity
        over the past 7 days
        """
        if date is None:
            date = timezone.now()
        date_since = date - datetime.timedelta(days=7)

        # Get daily hits objects
        daily_hits = QueryDailyHits.objects.filter(
            date__gte=date_since, date__lte=date)

        # Find most popular query strings
        most_popular = daily_hits.values('query_string').annotate(total_hits=models.Sum('hits')).order_by('-total_hits')

    @classmethod
    def get(cls, query_string):
        return cls(normalise_query_string(query_string))
