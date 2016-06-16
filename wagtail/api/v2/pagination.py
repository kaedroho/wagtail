from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from django.conf import settings
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .utils import BadRequestError


class WagtailPagination(BasePagination):
    def _make_link_url(self, request, new_offset):
        base_url = request.build_absolute_uri().split('?')[0]
        query_params = request.query_params.copy()

        if new_offset:
            query_params['offset'] = new_offset
        else:
            # Remove offset parameter
            query_params['offset'] = None
            del query_params['offset']

        if query_params:
            return base_url + '?' + query_params.urlencode()
        else:
            return base_url

    def paginate_queryset(self, queryset, request, view=None):
        limit_max = getattr(settings, 'WAGTAILAPI_LIMIT_MAX', 20)

        try:
            offset = int(request.GET.get('offset', 0))
            assert offset >= 0
        except (ValueError, AssertionError):
            raise BadRequestError("offset must be a positive integer")

        try:
            limit = int(request.GET.get('limit', min(20, limit_max)))

            if limit > limit_max:
                raise BadRequestError("limit cannot be higher than %d" % limit_max)

            assert limit >= 0
        except (ValueError, AssertionError):
            raise BadRequestError("limit must be a positive integer")

        start = offset
        stop = offset + limit

        self.view = view
        self.total_count = queryset.count()

        # Next/previous link headers
        is_aligned = offset % limit == 0
        self.links = OrderedDict()
        if is_aligned:
            self.links['first'] = self._make_link_url(request, 0)
            self.links['last'] = self._make_link_url(request, self.total_count // limit * limit)  # TODO: Rounds incorrectly when the total count is aligned

            if self.total_count > stop:
                self.links['next'] = self._make_link_url(request, offset + limit)

            if start - limit >= 0:
                max_offset = self.total_count // limit * limit  # TODO: Rounds incorrectly when the total count is aligned
                self.links['previous'] = self._make_link_url(request, min(start - limit, max_offset))

        return queryset[start:stop]

    def get_paginated_response(self, data):
        headers = {}

        if self.links:
            headers['Link'] = ', '.join(
                '<{url}>; rel="{rel}"'.format(
                    url=url,
                    rel=rel,
                )
                for rel, url in self.links.items()
            )

        print(headers)

        data = OrderedDict([
            ('meta', OrderedDict([
                ('total_count', self.total_count),
            ])),
            ('items', data),
        ])

        return Response(data, headers=headers)
