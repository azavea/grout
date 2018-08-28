import logging
from django.db import transaction
from django.conf import settings

import datetime
import json
import pytz
import requests

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from grout.models import Boundary, BoundaryPolygon, Record, RecordType, RecordSchema
from grout.serializer_fields import JsonBField, JsonSchemaField, GeomBBoxField

logger = logging.getLogger(__name__)


class RecordSerializer(GeoModelSerializer):

    data = JsonBField()

    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields = ('uuid',)


class RecordTypeSerializer(ModelSerializer):

    current_schema = serializers.SerializerMethodField()

    class Meta:
        model = RecordType
        fields = '__all__'

    def get_current_schema(self, obj):
        current_schema = obj.get_current_schema()
        uuid = None
        if current_schema:
            uuid = str(current_schema.uuid)
        return uuid


class RecordSchemaSerializer(ModelSerializer):

    schema = JsonSchemaField()

    def create(self, validated_data):
        """Creates new schema or creates new version and updates next_version of previous"""
        if validated_data['version'] > 1:  # Viewset's get_serializer() will always add 'version'
            with transaction.atomic():
                current = RecordSchema.objects.get(record_type=validated_data['record_type'],
                                                   next_version=None)
                new = RecordSchema.objects.create(**validated_data)
                current.next_version = new
                current.save()
        elif validated_data['version'] == 1:  # New record_type
            new = RecordSchema.objects.create(**validated_data)
        else:
            raise serializers.ValidationError('Schema version could not be determined')
        return new

    class Meta:
        model = RecordSchema
        fields = '__all__'
        read_only_fields = ('uuid', 'next_version')


class BoundaryPolygonSerializer(GeoFeatureModelSerializer):

    data = JsonBField()

    class Meta:
        model = BoundaryPolygon
        geo_field = 'geom'
        id_field = 'uuid'
        exclude = ('boundary',)


class BoundaryPolygonNoGeomSerializer(ModelSerializer):
    """Serialize a BoundaryPolygon without any geometry info"""
    data = JsonBField()
    bbox = GeomBBoxField(source='geom')

    class Meta:
        model = BoundaryPolygon
        exclude = ('geom',)


class BoundarySerializer(GeoModelSerializer):

    label = serializers.CharField(max_length=128, allow_blank=False)
    color = serializers.CharField(max_length=64, required=False)
    display_field = serializers.CharField(max_length=10, allow_blank=True, required=False)
    data_fields = JsonBField(read_only=True, allow_null=True)
    errors = JsonBField(read_only=True, allow_null=True)

    def create(self, validated_data):
        boundary = super(BoundarySerializer, self).create(validated_data)
        boundary.load_shapefile()
        return boundary

    class Meta:
        model = Boundary
        # These meta read_only/exclude settings only apply to the fields the ModelSerializer
        # instantiates for you by default. If you override a field manually, you need to override
        # all settings there.
        # e.g. adding 'errors' to this tuple has no effect, since we manually define the errors
        # field above
        read_only_fields = ('uuid', 'status',)
        fields = '__all__'
