from django.dispatch.dispatcher import receiver

from wagtail.wagtailsearch.views import search_view_served
from wagtail.wagtaileditorspicks.query import Query


@receiver(search_view_served)
def add_query_hit(request, query_string, **kwargs):
    if query_string:
        # Get query and add a hit
        query = Query.get(query_string).add_hit()
