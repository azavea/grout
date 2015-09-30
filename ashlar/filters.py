import json
import django_filters

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from dateutil.parser import parse

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filterset import GeoFilterSet

from ashlar.models import Boundary, BoundaryPolygon, Record, RecordType
from ashlar.exceptions import QueryParameterException


class RecordFilter(GeoFilterSet):

    record_type = django_filters.MethodFilter(name='record_type', action='filter_record_type')
    polygon = django_filters.MethodFilter(name='polygon', action='filter_polygon')

    def filter_polygon(self, queryset, geojson):
        """ Method filter for arbitrary polygon, sent in as geojson.
        """
        poly = GEOSGeometry(geojson)
        if poly.valid:
            return queryset.filter(geom__intersects=poly)
        else:
            raise ParseError('Input polygon must be valid GeoJSON: ' + poly.valid_reason)

    def filter_record_type(self, queryset, value):
        """ Method filter for records having a desired record type (uuid)

        e.g. /api/records/?record_type=44a51b83-470f-4e3d-b71b-e3770ec79772

        """
        return queryset.filter(schema__record_type=value)

    class Meta:
        model = Record
        fields = ['data', 'record_type', 'geom']


class RecordTypeFilter(django_filters.FilterSet):

    class Meta:
        model = RecordType
        fields = ['active']


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


class BoundaryPolygonFilter(GeoFilterSet):

    boundary = django_filters.MethodFilter(name='boundary', action='filter_boundary')

    def filter_boundary(self, queryset, value):
        """ Method filter for boundary polygons having a desired boundary (uuid)

        e.g. /api/boundarypolygons/?boundary=44a51b83-470f-4e3d-b71b-e3770ec79772

        """
        return queryset.filter(boundary=value)

    class Meta:
        model = BoundaryPolygon
        fields = ['data', 'boundary']


class DateRangeFilterBackend(BaseFilterBackend):
    """Used to filter querysets based on a given START_FIELD and END_FIELD

    NOTE: This filter must be inherited from in order to be used because
    1. its Meta class must be set with a model and list of fields
    2. you likely want to override START_FIELD/END_FIELD

    This is a simple filter which takes two (optional) limits and returns all records
    whose 'occurred_from' field falls on or between the maximum and minimum provided.
    If only a maximum or a minimum are provided, the MIN_DATETIME or MAX_DATETIME will
    be used instead.

    An example [truncated] query: /api/records/?occurred_min=1901-01-01T00:00:00+00:00Z
    """

    MIN_DATETIME = '1901-01-01T00:00:00+00:00'
    MAX_DATETIME = '9999-12-31T23:59:59.999999+00:00'

    FIELD = 'occurred_from'

    def filter_queryset(self, request, queryset, view):
        """Filter records by date

        Arguments
        :param request: django rest framework request instance
        :param queryset: queryset to apply filter to
        :param view: view that this filter is being used by

        QUERY PARAMS
        :param valid_from: ISO 8601 timestamp
        :param valid_to: ISO 8601 timestamp
        """
        occurred_min = 'occurred_min'
        occurred_max = 'occurred_max'
        err_msg = 'must be ISO 8601 formatted with timezone information. Please check that the URL is properly encoded.'
        if occurred_min not in request.query_params and occurred_max not in request.query_params:
            return queryset

        try:
            min_date = parse(request.query_params.get(occurred_min, self.MIN_DATETIME))
        except:
            raise QueryParameterException(occurred_min, err_msg)

        try:
            max_date = parse(request.query_params.get(occurred_max, self.MAX_DATETIME))
        except:
            raise QueryParameterException(occurred_max, err_msg)

        if not min_date.tzinfo or not max_date.tzinfo:
            raise QueryParameterException('datetimes', err_msg)

        return queryset.filter(occurred_from__gte=min_date, occurred_from__lte=max_date)


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

    EXAMPLE USAGE: /api/records/?jcontains={"Site": {"DPWH province name": "CAGAYAN"}}
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
