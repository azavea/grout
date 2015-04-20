import uuid

from django.contrib.gis.db import models

from django_pgjson.fields import JsonBField

class Record(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=64)
    schema = models.ForeignKey('RecordSchema')
    geometry = models.PointField(srid=4326)
    ## Unless we override db_index to always create a GIN index, we will need to have a migration
    #   that calls migrations.RunSQL("add index sql command here...")
    json_data = JsonBField()

    objects = models.GeoManager()

class RecordSchema(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.IntegerField()
    label = models.CharField(max_length=64)

    schema = JsonBField()
