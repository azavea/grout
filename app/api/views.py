from rest_framework import status, viewsets
from rest_framework.filters import DjangoFilterBackend
from rest_framework_gis.filters import InBBoxFilter

from ashlar.models import Boundary, Record, RecordSchema, ItemSchema
from serializers import (BoundarySerializer,
                         BoundaryListSerializer,
                         RecordSerializer,
                         RecordSchemaSerializer,
                         ItemSchemaSerializer)
from filters import BoundaryFilter, RecordFilter


class RecordViewSet(viewsets.ModelViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_class = RecordFilter
    bbox_filter_field = 'geom'
    filter_backends = (InBBoxFilter, DjangoFilterBackend)


class RecordSchemaViewSet(viewsets.ModelViewSet):

    queryset = RecordSchema.objects.all()
    serializer_class = RecordSchemaSerializer


class ItemSchemaViewSet(viewsets.ModelViewSet):

    queryset = ItemSchema.objects.all()
    serializer_class = ItemSchemaSerializer

class BoundaryViewSet(viewsets.ModelViewSet):

    queryset = Boundary.objects.all()
    filter_class = BoundaryFilter

    def get_serializer_class(self):
        return BoundaryListSerializer if self.action == 'list' else BoundarySerializer
