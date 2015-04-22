from django.core.exceptions import ValidationError
from django.test import TestCase

from api.serializer_fields import JsonBField, JsonSchemaField

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

        to_value = self.jsonb_field.to_representation([1,2,3])
        self.assertEqual(to_value, [1,2,3])

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
        self.invalid_schema = { "type": "any" }

    def test_to_representation(self):
        """ Pass through internal dict to dict, no transformation necessary """
        super(SerializerJsonSchemaFieldTestCase, self).test_to_representation()

    def test_to_internal_value(self):
        """ Ensure JsonSchemaField also validates schemas """
        super(SerializerJsonSchemaFieldTestCase, self).test_to_representation()

        to_value = self.json_schema_field.to_internal_value(self.valid_schema)
        self.assertEqual(to_value, self.valid_schema)

        with self.assertRaises(ValidationError):
            self.json_schema_field.to_internal_value(self.invalid_schema)
