from django.test import TestCase

import jsonschema

from ashlar.models import SchemaModel


class SchemaModelTestCase(TestCase):
    """Test SchemaModel abstract class"""

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

        # SchemaModel is an "abstract" class in database terms but that doesn't
        # prevent us from instantiating it without saving for testing purposes
        test_model = SchemaModel(schema=test_schema)

        self.assertIsNone(test_model.validate_json(valid))

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            test_model.validate_json(invalid)

    def test_validate_json_validates_schema(self):
        """Test that validating json will first validate the schema"""
        invalid_schema = {"type": "any"}
        valid_json = {}
        test_model = SchemaModel(schema=invalid_schema)

        with self.assertRaises(jsonschema.exceptions.SchemaError):
            test_model.validate_json(valid_json)
