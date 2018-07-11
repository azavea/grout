
from django.db import IntegrityError, transaction
from django.test import TestCase

from grout.models import RecordSchema, RecordType


class RecordSchemaTestCase(TestCase):

    def test_get_current_schema(self):
        """Ensure that duplicate versions of the same schema cannot exist"""
        record_type = RecordType.objects.create(label='foo', plural_label='foos')
        empty_record_type = RecordType.objects.create(label='empty', plural_label='empties')
        RecordSchema.objects.create(schema={}, version=1, record_type=record_type)
        RecordSchema.objects.create(schema={}, version=2, record_type=record_type)

        self.assertEqual(record_type.get_current_schema().version, 2)
        self.assertIsNone(empty_record_type.get_current_schema())
