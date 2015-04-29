from django.core.exceptions import ValidationError

from rest_framework.fields import Field

from jsonschema.exceptions import SchemaError

from ashlar.models import SchemaModel


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


class JsonSchemaField(JsonBField):
    """ Extend JsonBField to validate on conversion """

    type_name = 'JsonSchemaField'

    def to_internal_value(self, value):
        super(JsonSchemaField, self).to_internal_value(value)
        try:
            SchemaModel.validate_schema(value)
            return value
        except SchemaError as e:
            raise ValidationError('Invalid schema: {}'.format(e.message))
