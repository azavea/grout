from collections import OrderedDict

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from ashlar.models import Boundary, Record, RecordSchema, ItemSchema
from serializers import (BoundarySerializer,
                         BoundaryPolygonSerializer,
                         RecordSerializer,
                         RecordSchemaSerializer,
                         ItemSchemaSerializer)
from filters import BoundaryFilter, RecordFilter, JsonBFilterBackend


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


class RecordSchemaViewSet(viewsets.ModelViewSet):

    queryset = RecordSchema.objects.all()
    serializer_class = RecordSchemaSerializer
    jsonb_filter_field = 'schema'
    jsonb_filters = (
        ('jcontains', False),
    )
    filter_backends = (JsonBFilterBackend, DjangoFilterBackend)


class ItemSchemaViewSet(viewsets.ModelViewSet):

    queryset = ItemSchema.objects.all()
    serializer_class = ItemSchemaSerializer
    jsonb_filter_field = 'schema'
    jsonb_filters = (
        ('jcontains', False),
    )
    filter_backends = (JsonBFilterBackend, DjangoFilterBackend)


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
