from rest_framework.serializers import ModelSerializer

from ashlar.models import Record, RecordSchema, ItemSchema


class RecordSerializer(ModelSerializer):

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
