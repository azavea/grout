import json
import django_filters

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filterset import GeoFilterSet

from ashlar.models import Boundary, Record


class RecordFilter(GeoFilterSet):

    class Meta:
        model = Record
        fields = ['data']


class BoundaryFilter(GeoFilterSet):

    STATUS_SET = {status[0] for status in Boundary.StatusTypes.CHOICES}

    status = django_filters.MethodFilter(name='status', action='multi_filter_status')

    def multi_filter_status(self, queryset, value):
        """ Method filter for multiple choice query on status

        e.g. /api/boundary/?status=ERROR,WARNING

        """
        statuses = value.split(',')
        statuses = set(statuses) & self.STATUS_SET
        return queryset.filter(status__in=statuses)

    class Meta:
        model = Boundary
        fields = ['status']


class JsonBFilterBackend(BaseFilterBackend):
    """ Generic configurable filter for JsonBField

    Requires the following properties, configured on the view using this filter backend:

    jsonb_filter_field: The name of the django model field to filter against

    jsonb_filters: An iterable of tuples where each tuple takes the format:
    (lookup_field_name, allow_scalars)
    lookup_field_name: The lookup name of an available custom jsonb filter
    allow_scalars: True if the filter takes bool/string/int, otherwise False if array/object required
    e.g.
    (
        ('jcontains', False),
        ('jhas', True),
    )

    """
    def filter_queryset(self, request, queryset, view):
        """ Filter by configured jsonb_filters on jsonb_filter_field """
        filter_field = getattr(view, 'jsonb_filter_field', None)
        if not filter_field:
            raise ImproperlyConfigured('JsonBFilterBackend requires property ' +
                                       '`jsonb_filter_field` on view')

        jsonb_filters = getattr(view, 'jsonb_filters', None)
        if not jsonb_filters:
            raise ImproperlyConfigured('JsonBFilterBackend requires iterable property ' +
                                       '`jsonb_filters` on view')

        for jsonb_filter in jsonb_filters:
            if len(jsonb_filter) != 2:
                raise ImproperlyConfigured('Each jsonb_filter definition requires two ' +
                                           'properties. See documentation.')
            lookup_name = jsonb_filter[0]
            allow_scalars = jsonb_filter[1]
            filter_value = request.query_params.get(lookup_name, None)
            if not filter_value:
                continue

            filter_key = '{0}__{1}'.format(filter_field, lookup_name)
            try:
                json_data = json.loads(filter_value)
            except ValueError as e:
                raise ParseError(str(e))

            if allow_scalars or isinstance(json_data, dict) or isinstance(json_data, list):
                queryset = queryset.filter(Q(**{filter_key: json_data}))
            else:
                raise ParseError('Lookup must be an object or array')

        return queryset
