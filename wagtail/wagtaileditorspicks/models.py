from django.db import models
from django.utils import timezone

import datetime


class QueryDailyHits(models.Model):
    query_string = models.CharField(max_length=255, db_index=True)
    date = models.DateField()
    hits = models.IntegerField(default=0)

    @classmethod
    def garbage_collect(cls):
        """
        Deletes all QueryDailyHits records that are older than 7 days
        """
        min_date = timezone.now().date() - datetime.timedelta(days=7)

        cls.objects.filter(date__lt=min_date).delete()

    class Meta:
        unique_together = (
            ('query_string', 'date'),
        )


class EditorsPick(models.Model):
    query_string = models.CharField(max_length=255, db_index=True)
    page = models.ForeignKey('wagtailcore.Page', related_name='+')
    sort_order = models.IntegerField(null=True, blank=True, editable=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('sort_order', )
