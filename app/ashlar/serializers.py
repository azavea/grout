from collections import Iterable

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from ashlar.models import Boundary, BoundaryPolygon, Record, RecordSchema, ItemSchema
from ashlar.serializer_fields import JsonBField, JsonSchemaField


class RecordSerializer(GeoModelSerializer):

    data = JsonBField()

    class Meta:
        model = Record
        read_only_fields = ('uuid',)


class RecordSchemaSerializer(ModelSerializer):

    schema = JsonSchemaField()

    class Meta:
        model = RecordSchema
        read_only_fields = ('uuid',)


class ItemSchemaSerializer(ModelSerializer):

    schema = JsonSchemaField()

    class Meta:
        model = ItemSchema
        read_only_fields = ('uuid',)


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
