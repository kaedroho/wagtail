from django.db import models

from wagtail.wagtailsearch.models import Query


class EditorsPick(models.Model):
    query = models.ForeignKey(Query, db_index=True, related_name='editors_picks')
    page = models.ForeignKey('wagtailcore.Page', related_name='+')
    sort_order = models.IntegerField(null=True, blank=True, editable=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('sort_order', )
