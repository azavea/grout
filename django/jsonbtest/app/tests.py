from django.test import TestCase
from django.contrib.gis.geos import Point

from django_pgjson.fields import JsonBField

from app.models import Record, RecordSchema
# Must at least import the lookups once so that they are registered
#   There is very likely a better way to do this
import app.lookups

# Create your tests here.

class RecordTestCase(TestCase):

    def setUp(self):
        schema = RecordSchema.objects.create(version=1,
                                             label="FOOBAR",
                                             schema={"type": "jsonb"})
        Record.objects.create(label="FOOBAR",
                              schema=schema,
                              geometry=Point(0, 0, srid=4326),
                              json_data={
                                "data": {
                                    "foo": 7
                                },
                                "id": 2,
                                "list": ["apple", "orange", "banana"]
                              })

    def test_search_record_data(self):
        self.assertEqual(len(Record.objects.all()), 1)
        filtered_objects = Record.objects.filter(json_data__jcontains={"id": 2})
        self.assertEqual(len(filtered_objects), 1)
        filtered_objects = Record.objects.filter(json_data__jcontains={"data": {"foo": 7}})
        self.assertEqual(len(filtered_objects), 1)

    def test_exists_custom_lookup(self):
        filtered_objects = Record.objects.filter(json_data__jexists="list")
        self.assertEqual(len(filtered_objects), 1)


    def tearDown(self):
        pass