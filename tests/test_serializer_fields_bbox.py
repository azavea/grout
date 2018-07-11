from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.gis.geos import Polygon, MultiPolygon

from grout.serializer_fields import GeomBBoxField


class GeomBBoxFieldTestCase(TestCase):
    """ Test serializer field for JsonB """

    def setUp(self):
        self.bbox_field = GeomBBoxField()
        self.poly = MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))))

    def test_to_representation(self):
        rep = self.bbox_field.to_representation(self.poly)
        self.assertEqual(({"lat": 0.0, "lon": 0.0}, {"lat": 1.0, "lon": 1.0}), rep)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.bbox_field.to_representation("not a geometry")
