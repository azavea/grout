from dateutil.parser import parse
import json

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from ashlar.models import Record, RecordSchema, RecordType
from ashlar.views import RecordViewSet


class DateFilterBackendTestCase(TestCase):
    """ Test serializer field for dates """

    def setUp(self):
        try:
            self.user = User.objects.get(username='admin')
        except ObjectDoesNotExist:
            self.user = User.objects.create_user('admin',
                                                 'ashlar@azavea.com',
                                                 '123')

        self.factory = APIRequestFactory()
        self.queryset = RecordSchema.objects.all()

        self.item_type = RecordType.objects.create(label='item', plural_label='items')

        self.item_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Item",
            "description": "An item",
            "type": "object",
            "properties": {
                "id": {
                    "description": "The unique identifier for a product",
                    "type": "integer"
                },
                "name": {
                    "description": "Name of the product",
                    "type": "string"
                }
            },
            "required": ["id", "name"]
        }

        self.schema = RecordSchema.objects.create(record_type=self.item_type,
                                                  version=1,
                                                  schema=self.item_schema)

    def test_valid_datefilter(self):
        """ Test filtering on dates """
        self.assertEqual(len(self.queryset), 1)
        a_date       = parse('2015-01-01T00:00:00+00:00')
        a_later_date = parse('2015-02-22T00:00:00+00:00')

        Record.objects.create(
            occurred_from=a_date,  # A DATE
            occurred_to=a_date,
            geom='POINT (0 0)',
            schema=self.schema
        )
        Record.objects.create(
            occurred_from=a_later_date,  # A LATER DATE
            occurred_to=a_later_date,
            geom='POINT (0 0)',
            schema=self.schema
        )
        view = RecordViewSet.as_view({'get': 'list'})

        req1 = Request(self.factory.get('/foo/', {'occurred_max': a_date}))
        force_authenticate(req1, self.user)
        res1 = view(req1).render()
        self.assertEqual(json.loads(res1.content)['count'], 1)

        req2 = Request(self.factory.get('/foo/', {'occurred_max': a_later_date}))
        force_authenticate(req2, self.user)
        res2 = view(req2).render()
        self.assertEqual(json.loads(res2.content)['count'], 2)
