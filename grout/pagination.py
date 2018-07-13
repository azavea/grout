from rest_framework.pagination import LimitOffsetPagination, _positive_int


class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Allow client to request all by setting limit parameter to 'all'
    """
    # copied and lightly modified from:
    # https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/pagination.py#L350
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.count = self.get_count(queryset)

        # when requesting all records, set the limit to one more than the queryset count
        if self.limit == 'all':
            self.limit = self.count + 1

        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        return list(queryset[self.offset:self.offset + self.limit])

    # copied and lightly modified from:
    # https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/pagination.py#L370
    def get_limit(self, request):
        if self.limit_query_param:
            try:
                if request.query_params[self.limit_query_param] == 'all':
                    return 'all'
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit
