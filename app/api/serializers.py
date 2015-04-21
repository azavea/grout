from rest_framework.serializers import ModelSerializer

from rest_framework_gis.serializers import GeoModelSerializer

from ashlar.models import Record, RecordSchema, ItemSchema


class RecordSerializer(GeoModelSerializer):

    class Meta:
        model = Record
        read_only_fields = ('uuid',)


class RecordSchemaSerializer(ModelSerializer):

    class Meta:
        model = RecordSchema
        read_only_fields = ('uuid',)


class ItemSchemaSerializer(ModelSerializer):

    class Meta:
        model = ItemSchema
        read_only_fields = ('uuid',)
