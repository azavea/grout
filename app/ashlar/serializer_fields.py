from django.core.exceptions import ValidationError

from rest_framework.fields import Field

from ashlar.validators import validate_json_schema


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
    """Json Field that also validates whether it is a JSON-Schema"""
    type_name = 'JsonSchemaField'
    validators = [validate_json_schema]
