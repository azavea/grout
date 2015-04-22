import uuid

from django.contrib.gis.db import models
from django_pgjson.fields import JsonBField

import jsonschema

from django.conf import settings


class AshlarModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class SchemaModel(AshlarModel):
    version = models.IntegerField()
    schema = JsonBField()

    class Meta(object):
        abstract = True

    def validate_json(self, json_dict):
        """Validates a JSON-like dictionary against this object's schema

        :param json_dict: Python dict representing json to be validated against self.schema
        :return: None if validation succeeds; jsonschema.exceptions.ValidationError if failure
                 (or jsonschema.exceptions.SchemaError if the schema is invalid)
        """
        return jsonschema.validate(json_dict, self.schema)

    # TODO: May want to move to serializer
    def validate_schema(self, key, schema):
        """Validates that this object's schema is a valid JSON-Schema schema
        :param key: Name of the field being validated
        :param schema: Python dict representing json schema that should be checked
        :return: None if schema validates; raises jsonschema.exceptions.SchemaError
            if schema is invalid
        """
        jsonschema.Draft4Validator.check_schema(schema)


class Record(AshlarModel):
    """Spatiotemporal records -- e.g. Loch Ness Monster sightings, crime events, etc."""
    occurred_from = models.DateTimeField()
    occurred_to = models.DateTimeField()
    label = models.CharField(max_length=50)  # Human-readable
    slug = models.CharField(max_length=50)

    geom = models.PointField(srid=settings.ASHLAR_SRID)
    schema = models.ForeignKey('RecordSchema')
    data = JsonBField()

    objects = models.GeoManager()


class RecordSchema(SchemaModel):
    """Schemas for spatiotemporal records"""
    record_type = models.CharField(max_length=50)

    class Meta(object):
        unique_together = (('record_type', 'version'),)


class ItemSchema(SchemaModel):
    """Subschemas for logical "items" which can be included in Record data"""
    label = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, unique=True)

    class Meta(object):
        unique_together = (('slug', 'version'),)
