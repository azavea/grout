from django.db import IntegrityError, transaction
from django.test import TestCase

from grout.models import RecordSchema, RecordType


class RecordSchemaTestCase(TestCase):

    def test_no_duplicate_versions(self):
        """Ensure that duplicate versions of the same schema cannot exist"""
        record_type = RecordType.objects.create(label='foo', plural_label='foos')
        RecordSchema.objects.create(schema={}, record_type=record_type, version=1)
        with transaction.atomic():  # The IntegrityError will prevent further queries otherwise
            with self.assertRaises(IntegrityError):
                RecordSchema.objects.create(schema={}, record_type=record_type, version=1)

        RecordSchema.objects.create(schema={}, record_type=record_type, version=2)  # Should succeed
