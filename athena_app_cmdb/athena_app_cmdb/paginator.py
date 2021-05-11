from rest_framework import pagination
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    last_page_strings = ('last',)

    def get_paginated_response(self, data, item):
        return Response({
            item: data,
            'metadata': {
                'links': {'next': self.get_next_link(),
                          'previous': self.get_previous_link()},
                'count': self.page.paginator.count,
                'page': self.page.number,
                'numOfPages': self.page.paginator.num_pages
            }})


class MyPaginationMixin(object):
    @property
    def paginator(self):
        """
                The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, request):
        """
            Return a single page of results, or `None` if pagination
            is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, request, view=self)

    def get_paginated_response(self, data, datatype):
        """
            Return a paginated style `Response` object for the given
            output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, datatype)
