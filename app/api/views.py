from django.conf import settings

from rest_framework import viewsets

from ashlar.models import Record, RecordSchema, ItemSchema
from serializers import RecordSerializer, RecordSchemaSerializer, ItemSchemaSerializer


class RecordViewSet(viewsets.ModelViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer


class RecordSchemaViewSet(viewsets.ModelViewSet):

    queryset = RecordSchema.objects.all()
    serializer_class = RecordSchemaSerializer


class ItemSchemaViewSet(viewsets.ModelViewSet):

    queryset = ItemSchema.objects.all()
    serializer_class = ItemSchemaSerializer