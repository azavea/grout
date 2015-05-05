from collections import OrderedDict

from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from ashlar.models import Boundary, Record, RecordType, RecordSchema
from ashlar.serializers import (BoundarySerializer,
                                BoundaryPolygonSerializer,
                                RecordSerializer,
                                RecordTypeSerializer,
                                RecordSchemaSerializer)
from ashlar.filters import BoundaryFilter, RecordFilter, JsonBFilterBackend


class RecordViewSet(viewsets.ModelViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_class = RecordFilter
    bbox_filter_field = 'geom'
    jsonb_filter_field = 'data'
    jsonb_filters = (
        ('jcontains', False),
    )
    filter_backends = (InBBoxFilter, JsonBFilterBackend, DjangoFilterBackend)


class RecordTypeViewSet(viewsets.ModelViewSet):
    queryset = RecordType.objects.all()
    serializer_class = RecordTypeSerializer


class SchemaViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin):  # Schemas are immutable
    """Base ViewSet for viewsets displaying subclasses of SchemaModel"""


class RecordSchemaViewSet(SchemaViewSet):
    queryset = RecordSchema.objects.all()
    serializer_class = RecordSchemaSerializer
    jsonb_filter_field = 'schema'
    jsonb_filters = (
        ('jcontains', False),
    )
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
