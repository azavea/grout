import django_filters

from rest_framework_gis.filterset import GeoFilterSet

from ashlar.models import Record


class RecordFilter(GeoFilterSet):

    class Meta:
        model = Record