import os
import shutil
import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.gdal import DataSource as GDALDataSource
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinLengthValidator
from rest_framework import serializers

import jsonschema

from grout.imports.shapefile import (extract_zip_to_temp_dir,
                                     get_shapefiles_in_dir,
                                     make_multipolygon)
from grout.exceptions import GEOMETRY_TYPE_ERROR, DATETIME_REQUIRED, DATETIME_NOT_PERMITTED


class GroutModel(models.Model):
    """
    Base class providing attributes common to all Grout data types.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class RecordType(GroutModel):
    """
    Store metadata for a class of Records.
    """
    class GeometryType(object):
        POINT = 'point'
        POLYGON = 'polygon'
        MULTIPOLYGON = 'multipolygon'
        LINESTRING = 'linestring'
        NONE = 'none'
        CHOICES = (
            (POINT, 'Point'),
            (POLYGON, 'Polygon'),
            (MULTIPOLYGON, 'MultiPolygon'),
            (LINESTRING, 'LineString'),
            (NONE, 'None'),
        )

    label = models.CharField(max_length=64)
    plural_label = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    geometry_type = models.CharField(max_length=12,
                                     choices=GeometryType.CHOICES,
                                     default=GeometryType.POINT)
    temporal = models.BooleanField(default=True)

    def get_current_schema(self):
        schemas = self.schemas.order_by('-version')
        return schemas[0] if len(schemas) > 0 else None


class RecordSchema(GroutModel):
    """
    A flexible schema describing the data contained by a Record.
    """
    version = models.PositiveIntegerField()
    schema = JSONField()
    next_version = models.OneToOneField('self', related_name='previous_version', null=True,
                                        editable=False, on_delete=models.CASCADE)
    record_type = models.ForeignKey('RecordType',
                                    related_name='schemas',
                                    on_delete=models.CASCADE)

    class Meta(object):
        unique_together = (('record_type', 'version'),)

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


class Record(GroutModel):
    """
    An entity in the database. An entry of a given RecordType, following a
    schema defined by a certain RecordSchema.
    """
    schema = models.ForeignKey('RecordSchema', on_delete=models.CASCADE)
    data = JSONField(blank=True)  # `blank` lets us store empty dicts ({}).
    archived = models.BooleanField(default=False)
    occurred_from = models.DateTimeField(null=True, blank=True)
    occurred_to = models.DateTimeField(null=True, blank=True)
    geom = models.GeometryField(srid=settings.GROUT['SRID'], null=True, blank=True)
    location_text = models.CharField(max_length=200, null=True, blank=True)

    class Meta(object):
        ordering = ('-created',)

    def clean(self):
        """
        Provide custom field validation for this model.
        """
        errors = {}

        # Make sure that incoming geometry matches the geometry_type of the
        # RecordType for this Record.
        expected_geotype = self.schema.record_type.get_geometry_type_display()
        record_type_id = self.schema.record_type.uuid

        if self.geom:
            incoming_geotype = self.geom.geom_type
        else:
            incoming_geotype = 'None'

        if incoming_geotype != expected_geotype:
            geom_error = GEOMETRY_TYPE_ERROR.format(incoming=incoming_geotype,
                                                    expected=expected_geotype,
                                                    uuid=record_type_id)
            errors['geom'] = geom_error

        # Make sure that incoming datetime information matches the `temporal`
        # flag on the RecordType for this Record.
        datetime_required = self.schema.record_type.temporal

        if datetime_required:
            if self.occurred_from is None:
                occurred_from_error = DATETIME_REQUIRED.format(uuid=record_type_id)
                errors['occurred_from'] = occurred_from_error
            if self.occurred_to is None:
                occurred_to_error = DATETIME_REQUIRED.format(uuid=record_type_id)
                errors['occurred_to'] = occurred_to_error
        else:
            if self.occurred_from is not None:
                occurred_from_error = DATETIME_NOT_PERMITTED.format(uuid=record_type_id)
                errors['occurred_from'] = occurred_from_error
            if self.occurred_to is not None:
                occurred_to_error = DATETIME_NOT_PERMITTED.format(uuid=record_type_id)
                errors['occurred_to'] = occurred_to_error

        if errors.keys():
            # Raise a DRF ValidationError instead of a Django Core validation
            # error, since this exception needs to get handled by the serializer.
            raise serializers.ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Extend the model's save method to run custom field validators.
        """
        self.clean()
        return super(Record, self).save(*args, **kwargs)


class Boundary(GroutModel):
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
    label = models.CharField(max_length=128, unique=True, validators=[MinLengthValidator(3)])
    # Store any valid css color string
    color = models.CharField(max_length=64, default='blue')
    display_field = models.CharField(max_length=10, blank=True, null=True)
    data_fields = JSONField(blank=True, null=True)
    errors = JSONField(blank=True, null=True)
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
                feature.geom.transform(settings.GROUT['SRID'])
                geometry = make_multipolygon(feature.geom)
                data = {field: feature.get(field) for field in self.data_fields}
                self.polygons.create(geom=geometry, data=data)

            self.status = self.StatusTypes.COMPLETE
            self.save()
        except Exception as e:
            if self.errors is None:
                self.errors = {}
            self.errors['message'] = str(e)
            # Relabel geography to allow saving a valid shapefile in this namespace
            self.label = self.label + '_' + str(uuid.uuid4())
            self.status = self.StatusTypes.ERROR
            self.save()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class BoundaryPolygon(GroutModel):
    """ Individual boundaries and associated data for each geom in a BoundaryUpload """

    boundary = models.ForeignKey('Boundary',
                                 related_name='polygons',
                                 null=True,
                                 on_delete=models.CASCADE)
    data = JSONField()
    geom = models.MultiPolygonField(srid=settings.GROUT['SRID'])
