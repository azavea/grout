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

    # TODO: How do we automagically detect that this is a nullable field and
    #   set allow_null accordingly?
    #   I guess we could just create a NullJsonBField instead?
    errors = JsonBField(allow_null=True)

    class Meta:
        model = Boundary
        read_only_fields = ('uuid', 'status', 'errors', 'geom',)
