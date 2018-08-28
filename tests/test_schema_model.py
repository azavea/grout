from django.test import TestCase

import jsonschema

from grout.models import RecordSchema


class SchemaModelTestCase(TestCase):
    """
    Test methods of the RecordSchema class related to modelling schemas.
    """
    def test_validate_json(self):
        """
        Ensure that the validation function returns None / raises on invalid.
        """
        # Lifted directly from the python-jsonschema docs
        test_schema = {"type": "object",
                       "properties": {
                           "price": {"type": "number"},
                           "name": {"type": "string"},
                       }}
        valid = {"name": "Eggs", "price": 34.99}
        invalid = {"name": "Eggs", "price": "Invalid"}

        test_model = RecordSchema(schema=test_schema)

        self.assertIsNone(test_model.validate_json(valid))

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            test_model.validate_json(invalid)

    def test_validate_json_validates_schema(self):
        """
        Test that validating json will first validate the schema.
        """
        invalid_schema = {"type": "any"}
        valid_json = {}
        test_model = RecordSchema(schema=invalid_schema)

        with self.assertRaises(jsonschema.exceptions.SchemaError):
            test_model.validate_json(valid_json)
