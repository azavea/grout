from collections import OrderedDict

from django.db import IntegrityError
from dateutil.parser import parse

from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import detail_route
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework_gis.filters import InBBoxFilter

from grout import exceptions
from grout.models import (Boundary,
                          BoundaryPolygon,
                          Record,
                          RecordType,
                          RecordSchema)
from grout.serializers import (BoundarySerializer,
                               BoundaryPolygonSerializer,
                               BoundaryPolygonNoGeomSerializer,
                               RecordSerializer,
                               RecordTypeSerializer,
                               RecordSchemaSerializer)
from grout.filters import (BoundaryFilter,
                           BoundaryPolygonFilter,
                           JsonBFilterBackend,
                           RecordFilter,
                           RecordTypeFilter)

from grout.pagination import OptionalLimitOffsetPagination


class BoundaryPolygonViewSet(viewsets.ModelViewSet):

    queryset = BoundaryPolygon.objects.all()
    serializer_class = BoundaryPolygonSerializer
    filter_class = BoundaryPolygonFilter
    pagination_class = OptionalLimitOffsetPagination
    bbox_filter_field = 'geom'
    jsonb_filter_field = 'data'
    filter_backends = (InBBoxFilter, JsonBFilterBackend, DjangoFilterBackend)

    def get_serializer_class(self):
        if 'nogeom' in self.request.query_params and self.request.query_params['nogeom']:
            return BoundaryPolygonNoGeomSerializer
        return BoundaryPolygonSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_class = RecordFilter
    bbox_filter_field = 'geom'
    jsonb_filter_field = 'data'
    filter_backends = (InBBoxFilter, JsonBFilterBackend, DjangoFilterBackend)

    def get_queryset(self):
        """
        Validate the input parameters before returning the queryset.
        """
        occurred_min = self.request.query_params.get('occurred_min', None)
        occurred_max = self.request.query_params.get('occurred_max', None)

        # Make sure that occurred_min < occurred_max if both params exist.
        if occurred_min and occurred_max:
            # Parse both dates in order to compare them.
            try:
                min_date = parse(occurred_max)
            except ValueError:
                # The parser could not parse the date string, so raise an error.
                raise exceptions.QueryParameterException('occurred_max',
                                                         exceptions.DATETIME_FORMAT_ERROR)

            try:
                max_date = parse(occurred_max)
            except ValueError:
                raise exceptions.QueryParameterException('occurred_max',
                                                         exceptions.DATETIME_FORMAT_ERROR)

            if occurred_min > occurred_max:
                messages = {
                    'occurred_min': exceptions.MIN_DATE_RANGE_FILTER_ERROR,
                    'occurred_max': exceptions.MAX_DATE_RANGE_FILTER_ERROR
                }
                raise serializers.ValidationError(messages)

        return self.queryset


class RecordTypeViewSet(viewsets.ModelViewSet):
    queryset = RecordType.objects.all()
    serializer_class = RecordTypeSerializer
    filter_class = RecordTypeFilter
    pagination_class = OptionalLimitOffsetPagination
    ordering = ('plural_label',)


class SchemaViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin):  # Schemas are immutable
    """Base ViewSet for viewsets displaying subclasses of SchemaModel"""
    pagination_class = OptionalLimitOffsetPagination


class RecordSchemaViewSet(SchemaViewSet):
    queryset = RecordSchema.objects.all()
    serializer_class = RecordSchemaSerializer
    jsonb_filter_field = 'schema'
    filter_backends = (JsonBFilterBackend, DjangoFilterBackend)

    # N.B. The DRF documentation is misleading; if you include named parameters as
    # shown in the documentation, this will cause list and detail endpoints to
    # throw Serializer errors.
    def get_serializer(self, *args, **kwargs):
        """Override data passed to serializer with incremented version if necessary"""
        if self.action == 'create' and 'data' in kwargs and 'record_type' in kwargs['data']:
            try:
                version = RecordSchema.objects.get(record_type=kwargs['data']['record_type'],
                                                   next_version=None).version + 1
            except RecordSchema.DoesNotExist:
                version = 1
            kwargs['data']['version'] = version
        return super(RecordSchemaViewSet, self).get_serializer(*args, **kwargs)


class BoundaryViewSet(viewsets.ModelViewSet):

    queryset = Boundary.objects.all()
    serializer_class = BoundarySerializer
    filter_class = BoundaryFilter
    pagination_class = OptionalLimitOffsetPagination
    ordering = ('display_field',)

    def create(self, request, *args, **kwargs):
        """Overwritten to allow use of semantically important/appropriate status codes for
        informing users about the type of error they've encountered
        """
        try:
            return super(BoundaryViewSet, self).create(request, *args, **kwargs)
        except IntegrityError:
            return Response({'error': 'uniqueness constraint violation'}, status.HTTP_409_CONFLICT)

    @detail_route(methods=['get'])
    def geojson(self, request, pk=None):
        """ Print boundary polygons as geojson FeatureCollection

        Pretty non-performant, and geojson responses get large quickly.
        TODO: Consider other solutions

        """
        boundary = self.get_object()
        polygons = boundary.polygons.values()
        serializer = BoundaryPolygonSerializer()
        features = [serializer.to_representation(polygon) for polygon in polygons]
        data = OrderedDict((
            ('type', 'FeatureCollection'),
            ('features', features)
        ))
        return Response(data)
