from django.test import TestCase

import jsonschema

from grout.models import RecordSchema, SchemaModel


class SchemaModelTestCase(TestCase):
    """Test SchemaModel abstract class"""
    def test_class_hierarchy(self):
        """Make sure that RecordSchema is a subclass of SchemaModel"""
        # Because we use it as a non-abstract stand-in for SchemaModel
        # throughout these tests
        self.assertTrue(issubclass(RecordSchema, SchemaModel))

    def test_validate_json(self):
        """Ensure that the validation function returns None / raises on invalid"""
        # Lifted directly from the python-jsonschema docs
        test_schema = {"type": "object",
                       "properties": {
                           "price": {"type": "number"},
                           "name": {"type": "string"},
                       }}
        valid = {"name": "Eggs", "price": 34.99}
        invalid = {"name": "Eggs", "price": "Invalid"}

        # We have to use a RecordSchema here because SchemaModel itself is
        # abstract and the ForeignKey to 'self' prevents it from being
        # instantiated.
        test_model = RecordSchema(schema=test_schema)

        self.assertIsNone(test_model.validate_json(valid))

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            test_model.validate_json(invalid)

    def test_validate_json_validates_schema(self):
        """Test that validating json will first validate the schema"""
        invalid_schema = {"type": "any"}
        valid_json = {}
        test_model = RecordSchema(schema=invalid_schema)

        with self.assertRaises(jsonschema.exceptions.SchemaError):
            test_model.validate_json(valid_json)
