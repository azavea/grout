from collections import OrderedDict
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.db.models import Value
from django.contrib.gis.db import models

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework_gis.filters import InBBoxFilter

from grout.models import (Boundary,
                          BoundaryPolygon,
                          Record,
                          PointRecord,
                          PolygonRecord,
                          FlexibleRecord,
                          TemporalPolygonRecord,
                          TemporalFlexibleRecord,
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
                           RecordTypeFilter,
                           DateRangeFilterBackend)

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
    serializer_class = RecordSerializer
    filter_class = RecordFilter
    bbox_filter_field = 'geom'
    jsonb_filter_field = 'data'
    filter_backends = (InBBoxFilter, JsonBFilterBackend, DateRangeFilterBackend)

    VALID_GEOTYPES = ['point', 'polygon', 'none']
    GEOTYPE_NOT_VALID = "The 'geometry_type' parameter must be one of: " + ', '.join(VALID_GEOTYPES)
    BAD_GEOMETRY = "The posted geometry was parsed as a {input}, when it should be a {expected}."
    GEOTYPE_AND_POLYGON = ("The 'geometry_type' parameter cannot be 'none' when " +
                           "either of the 'polygon' or 'polygon_id' parameters is present.")
    INVALID_DATETIMES = "'{none}' cannot be 'none' when '{timestamp}' is a timestamp."

    def get_queryset(self):
        '''
        Check for the `geometry_type` and `occurred_min`/`occurred_max`
        query parameters. If they exist, use them to generate a queryset for
        the appropriate class of Record.
        '''
        # Parse query parameters that can have an effect on the base queryset.
        geometry_type = self.request.query_params.get('geometry_type')
        occurred_min = self.request.query_params.get('occurred_min')
        occurred_max = self.request.query_params.get('occurred_max')
        polygon = self.request.query_params.get('polygon')
        polygon_id = self.request.query_params.get('polygon_id')

        # If one of the datetime parameters is 'none', make sure that the other
        # is not a timestamp.
        if occurred_min == 'none' and (occurred_max is not None and occurred_max != 'none'):
            raise ParseError(self.INVALID_DATETIMES.format(none='occurred_min',
                                                           timestamp='occurred_max'))
        elif occurred_max == 'none' and (occurred_min is not None and occurred_min != 'none'):
            raise ParseError(self.INVALID_DATETIMES.format(none='occurred_max',
                                                           timestamp='occurred_min'))

        # Temporal Records are the default, so only filter by nontemporal records
        # if a 'none' parameter is explicitly set.
        filtering_by_time = occurred_min != 'none' and occurred_max != 'none'

        if geometry_type:
            # Check that the geometry_type parameter is valid.
            if geometry_type not in self.VALID_GEOTYPES:
                raise ParseError(self.GEOTYPE_NOT_VALID)

            if geometry_type == 'none':
                if polygon is not None or polygon_id is not None:
                    # The user cannot request non-geospatial records and also
                    # attempt to filter by a geometry.
                    raise ParseError(self.GEOTYPE_AND_POLYGON)

                if filtering_by_time:
                    return TemporalFlexibleRecord.objects.all()
                else:
                    return FlexibleRecord.objects.all()

            elif geometry_type == 'polygon':
                if filtering_by_time:
                    return TemporalPolygonRecord.objects.all()
                else:
                    return PolygonRecord.objects.all()

            elif geometry_type == 'point':
                if filtering_by_time:
                    return Record.objects.all()
                else:
                    return PointRecord.objects.all()

            else:
                # Since we validated the geometry_type parameters earlier, it
                # should be impossible to reach this portion of the code. However,
                # for the sake of safety, raise an error if the parameter is
                # somehow unhandled.
                raise ParseError(self.GEOTYPE_NOT_VALID)
        else:
            # If no `geometry_type` is specified, the Record (Point) class is
            # the default queryset.
            if filtering_by_time:
                return Record.objects.all()
            else:
                return PointRecord.objects.all()


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
