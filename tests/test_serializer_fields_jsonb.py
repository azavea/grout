from django.core.exceptions import ValidationError
from django.test import TestCase

from grout.serializer_fields import (JsonBField, JsonSchemaField, MethodTransformJsonField,
                                     DropJsonKeyException)
from grout.validators import validate_json_schema


class SerializerJsonBFieldTestCase(TestCase):
    """ Test serializer field for JsonB """

    def setUp(self):
        self.jsonb_field = JsonBField()
        self.valid = {"name": "Eggs", "price": 34.99}

    def test_to_representation(self):
        """ Pass through internal dict to dict, no transformation necessary """
        to_value = self.jsonb_field.to_representation(self.valid)
        self.assertEqual(to_value, self.valid)

        to_value = self.jsonb_field.to_representation(3)
        self.assertEqual(to_value, 3)

        to_value = self.jsonb_field.to_representation(None)
        self.assertEqual(to_value, None)

        to_value = self.jsonb_field.to_representation([1, 2, 3])
        self.assertEqual(to_value, [1, 2, 3])

    def test_to_internal_value(self):
        """ Check valid json passed when converting

        list and dict are valid,
        string/int/null invalid

        """
        to_value = self.jsonb_field.to_internal_value(self.valid)
        self.assertEqual(to_value, self.valid)

        to_value = self.jsonb_field.to_internal_value([])
        self.assertEqual(to_value, [])

        with self.assertRaises(ValidationError):
            self.jsonb_field.to_internal_value(None)

        with self.assertRaises(ValidationError):
            self.jsonb_field.to_internal_value(3)

        with self.assertRaises(ValidationError):
            self.jsonb_field.to_internal_value('invalid')

    def test_allow_null_jsonb_field(self):
        """ Ensure falsy values convert to None, except empty objects/arrays """
        null_jsonb_field = JsonBField(allow_null=True)
        to_value = null_jsonb_field.to_internal_value(None)
        self.assertEqual(to_value, None)

        to_value = null_jsonb_field.to_internal_value('')
        self.assertEqual(to_value, None)

        to_value = null_jsonb_field.to_internal_value({})
        self.assertEqual(to_value, {})

        to_value = null_jsonb_field.to_internal_value([])
        self.assertEqual(to_value, [])


class SerializerJsonSchemaFieldTestCase(SerializerJsonBFieldTestCase):
    """ Test serializer field for json schema """

    def setUp(self):
        super(SerializerJsonSchemaFieldTestCase, self).setUp()
        self.json_schema_field = JsonSchemaField()
        self.valid_schema = {"type": "object",
                             "properties": {
                                 "price": {"type": "number"},
                                 "name": {"type": "string"},
                             }}

    def test_to_representation(self):
        """ Pass through internal dict to dict, no transformation necessary """
        super(SerializerJsonSchemaFieldTestCase, self).test_to_representation()

    def test_to_internal_value(self):
        """ Ensure JsonSchemaField also validates schemas """
        super(SerializerJsonSchemaFieldTestCase, self).test_to_representation()

        to_value = self.json_schema_field.to_internal_value(self.valid_schema)
        self.assertEqual(to_value, self.valid_schema)

    def test_has_schema_validator(self):
        """Make sure JsonSchemaField has the proper validator"""
        self.assertIn(validate_json_schema, self.json_schema_field.validators)


class JsonSchemaValidatorTestCase(TestCase):
    """Test JSON schema validation"""
    def setUp(self):
        self.invalid_schema = {"type": "any"}

    def test_schema_validation(self):
        """Ensure that JSON Schema validation is properly wrapped in a ValidationError"""
        with self.assertRaises(ValidationError):
            validate_json_schema(self.invalid_schema)


class MethodTransformJsonFieldTestCase(TestCase):
    """Test transformed JSON field"""
    def setUp(self):
        self.test_json = {"dict": dict(), "foo": dict(), "list": [], "num": 5,
                          "bool": True, "string": "Foo"}

    def transform_val_is_dict(self, key, value):
        """Returns the value if it is a dict, raises DropJsonKeyException otherwise"""
        if isinstance(value, dict):
            return key, value
        else:
            raise DropJsonKeyException

    def transform_append_str(self, key, value):
        """Returns the value unaltered unless it's a string in which case "transform" is appended"""
        if isinstance(value, str):
            return key, value + "transform"
        else:
            return key, value

    def test_drop_keys(self):
        """Test that transform method can drop keys."""
        dict_only_filter = MethodTransformJsonField('transform_val_is_dict')
        # Bind to self so the field can find the rigth method, even though self isn't a serializer
        dict_only_filter.bind('field name here in real life', self)

        transformed = dict_only_filter.to_representation(self.test_json)
        self.assertEqual(transformed, {"dict": {}, "foo": {}})

    def test_transform_values(self):
        """Test that transform method can transform values."""
        append_str = MethodTransformJsonField('transform_append_str')
        append_str.bind('field name here in real life', self)
        transformed = append_str.to_representation(self.test_json)
        # "Foo" should have had "transform" appended.
        self.assertEqual(transformed, {"dict": dict(), "foo": dict(), "list": [], "num": 5,
                                       "bool": True, "string": "Footransform"})
