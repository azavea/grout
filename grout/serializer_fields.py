from six import iteritems
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry

from rest_framework.fields import Field

from grout.validators import validate_json_schema


class JsonBField(Field):
    """ Custom serializer class for JsonB

    Do no transformations, as we always want python dicts
    Ensure top level is an object or array

    """
    type_name = 'JsonBField'

    def to_representation(self, value):
        return value

    def to_internal_value(self, value):
        if isinstance(value, dict) or isinstance(value, list):
            return value
        elif self.allow_null and not value:
            return None
        else:
            raise ValidationError('Array or object required')


class DropJsonKeyException(Exception):
    """A way for JSON transformation functions to signal that a field should be dropped.

    Raising this exception from a transform function does not imply an error condition, but rather
    signals to the MethodTransformJsonField that the key/value pair passed to the transformation
    function should be omitted from the response.
    """
    pass


class MethodTransformJsonField(Field):
    """Custom field to filter JSON fields by serializer method before returning

    Must be supplied the name of a filter_method on initialization. The filter_method
    must be a method on the parent serializer and will be passed two parameters:
        - key (the key at the root level of the JSON object)
        - val (the value associated with key)
    filter_method should return a transformed version of value, or raise a DropJsonKeyException
    to specify that the key/value pair should be dropped from the response.
    """
    # Loosely adapted from DRF's SerializerMethodField
    type_name = 'MethodFilteredJsonField'

    def __init__(self, transform_method_name=None, **kwargs):
        self.transform_method_name = transform_method_name
        kwargs['read_only'] = True
        super(MethodTransformJsonField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        default_transform = 'transform_{field_name}'.format(field_name=field_name)
        if self.transform_method_name is None:
            self.transform_method_name = default_transform
        super(MethodTransformJsonField, self).bind(field_name, parent)

    def to_representation(self, value):
        """Transforms value's root-level key/value pairs based on parent.transform_method_name

        Assumes value is a dict.
        """
        transform_method = getattr(self.parent, self.transform_method_name)
        representation = {}
        for key, val in iteritems(value):
            try:
                (new_key, new_val) = transform_method(key, val)
                representation[new_key] = new_val
            except DropJsonKeyException:
                continue
        return representation


class JsonSchemaField(JsonBField):
    """Json Field that also validates whether it is a JSON-Schema"""
    type_name = 'JsonSchemaField'
    validators = [validate_json_schema]


class GeomBBoxField(Field):
    """Serialize a geometry as a bounding box"""
    read_only = True

    def to_representation(self, value):
        if not (issubclass(value.__class__, GEOSGeometry)):
            msg = 'Can\'t apply GeomBBoxField to non-Geometry class {cls}'
            raise ValidationError(msg.format(cls=value.__class__.__name__))
        xmin, ymin, xmax, ymax = value.extent
        return ({"lon": xmin, "lat": ymin}, {"lon": xmax, "lat": ymax})
