import os
import shutil
import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.gdal import DataSource as GDALDataSource
from django_pgjson.fields import JsonBField

import jsonschema

from ashlar.imports.shapefile import (extract_zip_to_temp_dir,
                                      get_shapefiles_in_dir,
                                      make_multipolygon)


class AshlarModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class SchemaModel(AshlarModel):
    version = models.PositiveIntegerField()
    schema = JsonBField()
    next_version = models.OneToOneField('self', related_name='previous_version', null=True,
                                        editable=False)

    class Meta(object):
        abstract = True

    def validate_json(self, json_dict):
        """Validates a JSON-like dictionary against this object's schema

        :param json_dict: Python dict representing json to be validated against self.schema
        :return: None if validation succeeds; jsonschema.exceptions.ValidationError if failure
                 (or jsonschema.exceptions.SchemaError if the schema is invalid)
        """
        return jsonschema.validate(json_dict, self.schema)

    @classmethod
    def validate_schema(self, schema):
        """Validates that this object's schema is a valid JSON-Schema schema
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

    geom = models.PointField(srid=settings.ASHLAR['SRID'])
    schema = models.ForeignKey('RecordSchema')
    data = JsonBField()

    objects = models.GeoManager()


class RecordType(AshlarModel):
    """ Store extra information for a given RecordType, associated schemas in RecordSchema """
    label = models.CharField(max_length=64)
    plural_label = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    def get_current_schema(self):
        schemas = self.schemas.order_by('-version')
        return schemas[0] if len(schemas) > 0 else None


class RecordSchema(SchemaModel):
    """Schemas for spatiotemporal records"""
    record_type = models.ForeignKey('RecordType', related_name='schemas')

    class Meta(object):
        unique_together = (('record_type', 'version'),)


class Boundary(AshlarModel):
    """ MultiPolygon objects which contain related geometries for filtering/querying """

    class StatusTypes(object):
        PENDING = 'PENDING'
        PROCESSING = 'PROCESSING'
        ERROR = 'ERROR'
        WARNING = 'WARNING'
        COMPLETE = 'COMPLETE'
        CHOICES = (
            (PENDING, 'Pending'),
            (PROCESSING, 'Processing'),
            (WARNING, 'Warning'),
            (ERROR, 'Error'),
            (COMPLETE, 'Complete'),
        )

    status = models.CharField(max_length=10,
                              choices=StatusTypes.CHOICES,
                              default=StatusTypes.PENDING)
    label = models.CharField(max_length=64)
    # Store any valid css color string
    color = models.CharField(max_length=64, default='blue')
    display_field = models.CharField(max_length=10, blank=True, null=True)
    data_fields = JsonBField(blank=True, null=True)
    errors = JsonBField(blank=True, null=True)
    source_file = models.FileField(upload_to='boundaries/%Y/%m/%d')

    def load_shapefile(self):
        """ Validate the shapefile saved on disk and load into db """
        self.status = self.StatusTypes.PROCESSING
        self.save()

        try:
            temp_dir = extract_zip_to_temp_dir(self.source_file)
            shapefiles = get_shapefiles_in_dir(temp_dir)

            if len(shapefiles) != 1:
                raise ValueError('Exactly one shapefile (.shp) required')

            shapefile_path = os.path.join(temp_dir, shapefiles[0])
            shape_datasource = GDALDataSource(shapefile_path)
            if len(shape_datasource) > 1:
                raise ValueError('Shapefile must have exactly one layer')

            boundary_layer = shape_datasource[0]
            if boundary_layer.srs is None:
                raise ValueError('Shapefile must include a .prj file')
            self.data_fields = boundary_layer.fields
            for feature in boundary_layer:
                feature.geom.transform(settings.ASHLAR['SRID'])
                geometry = make_multipolygon(feature.geom)
                data = {field: feature.get(field) for field in self.data_fields}
                self.polygons.create(geom=geometry, data=data)

            self.status = self.StatusTypes.COMPLETE
            self.save()
        except Exception as e:
            if self.errors is None:
                self.errors = {}
            self.errors['message'] = str(e)
            self.status = self.StatusTypes.ERROR
            self.save()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class BoundaryPolygon(AshlarModel):
    """ Individual boundaries and associated data for each geom in a BoundaryUpload """

    boundary = models.ForeignKey('Boundary', related_name='polygons', null=True)
    data = JsonBField()
    geom = models.MultiPolygonField(srid=settings.ASHLAR['SRID'])

    objects = models.GeoManager()
