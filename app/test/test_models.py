import jsonschema

from ashlar.ashlar.models import SchemaModel
from ashlar.ashlar.exceptions import SchemaException

from base import AshlarTestCase


class SchemaTestCase(AshlarTestCase):
    """Test SchemaModel abstract class"""

    def test_validate_json(self):
        """Ensure that the validation function returns None / raises on invalid"""
        # Instantiating a base model won't work if we save it to the DB, but
        # that's not necessary to test that the validation functions work.
        # Lifted directly from the python-jsonschema docs
        test_schema = {"type": "object",
                       "properties": {
                           "price": {"type": "number"},
                           "name": {"type": "string"},
                       }}
        valid = {"name": "Eggs", "price": 34.99}
        invalid = {"name": "Eggs", "price": "Invalid"}
        test_model = SchemaModel(schema=test_schema)

        self.assertIsNone(test_model.validate_json(valid))

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            test_model.validate_json(invalid)

    def test_validate_schema(self):
        """Ensure that bad schemas don't validate"""
        bad_schema = {"type": "any"}
        test_model = SchemaModel()

        with self.assertRaises(SchemaException):
            test_model.validate_schema('schema', bad_schema)

    def test_validate_returns(self):
        """Ensure that a valid schema is returned by the validation function"""
        good_schema = {"type": "object"}
        test_model = SchemaModel()
        self.assertEqual(good_schema, test_model.validate_schema('schema', good_schema))
