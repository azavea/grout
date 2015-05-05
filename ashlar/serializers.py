from django.db import transaction

from rest_framework import fields
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from ashlar.models import Boundary, BoundaryPolygon, Record, RecordType, RecordSchema
from ashlar.serializer_fields import JsonBField, JsonSchemaField


class RecordSerializer(GeoModelSerializer):

    data = JsonBField()

    class Meta:
        model = Record
        read_only_fields = ('uuid',)


class RecordTypeSerializer(ModelSerializer):

    class Meta:
        model = RecordType


class SchemaSerializer(ModelSerializer):
    """Base class for serializers of subclasses of models.SchemaModel"""
    schema = JsonSchemaField()


class RecordSchemaSerializer(SchemaSerializer):

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
        read_only_fields = ('uuid', 'next_version')


class BoundaryPolygonSerializer(GeoFeatureModelSerializer):

    data = JsonBField()

    class Meta:
        model = BoundaryPolygon
        geo_field = 'geom'
        id_field = 'uuid'
        exclude = ('boundary',)


class BoundarySerializer(GeoModelSerializer):

    color = serializers.CharField(max_length=64)
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
