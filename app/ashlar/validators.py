from django.core.exceptions import ValidationError

import jsonschema
from jsonschema.exceptions import SchemaError


def validate_json_schema(value):
    """Wrap jsonschema validation with serializers.ValidationError"""
    try:
        jsonschema.Draft4Validator.check_schema(value)
    except SchemaError as e:
        raise ValidationError('Invalid schema: {}'.format(e.message))
