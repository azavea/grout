from django.db import IntegrityError, transaction
from django.test import TestCase

from ashlar.models import ItemSchema


class ItemSchemaTestCase(TestCase):

    def test_no_duplicate_slugs(self):
        """Ensure that duplicate versions of the same schema cannot exist"""
        ItemSchema.objects.create(schema={}, slug='item', version=1)
        with transaction.atomic():  # The IntegrityError will prevent further queries otherwise
            with self.assertRaises(IntegrityError):
                ItemSchema.objects.create(schema={}, slug='item', version=1)

        with transaction.atomic():  # The IntegrityError will prevent further queries otherwise
            with self.assertRaises(IntegrityError):
                ItemSchema.objects.create(schema={}, slug='item', version=2)

        ItemSchema.objects.create(schema={}, slug='different_item', version=1)  # Should succeed
