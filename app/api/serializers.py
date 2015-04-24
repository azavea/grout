from collections import Iterable

from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoModelSerializer

from ashlar.models import Boundary, Record, RecordSchema, ItemSchema
from serializer_fields import JsonBField, JsonSchemaField


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


class BoundarySerializer(GeoModelSerializer):

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
        read_only_fields = ('uuid', 'status', 'geom',)


class BoundaryListSerializer(BoundarySerializer):

    class Meta:
        # Need to redefine model, but not other properties?
        model = Boundary
        exclude = ('geom',)