import logging
from django.db import transaction
from django.conf import settings

import datetime
import json
import pytz
import requests

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from grout.models import Boundary, BoundaryPolygon, Record, RecordType, RecordSchema
from grout.serializer_fields import JsonBField, JsonSchemaField, GeomBBoxField

logger = logging.getLogger(__name__)


class RecordSerializer(GeoModelSerializer):

    data = JsonBField()

    def create(self, validated_data):
        """Override create, so we can set empty weather data"""
        self.set_empty_weather_data(validated_data)
        record = super(RecordSerializer, self).create(validated_data)
        return record

    def update(self, record, validated_data):
        """Override update, so we can set empty weather data"""
        self.set_empty_weather_data(validated_data)
        return super(RecordSerializer, self).update(record, validated_data)

    def set_empty_weather_data(self, data):
        """Checks if weather data is empty, and if so, sets it using forecast.io

        :param data: Python dict representing record to be saved
        """
        # Only request data from forecast.io if an API key is configured and weather data is missing
        forecast_io_key = settings.FORECAST_IO_API_KEY
        weather = data.get('weather')
        light = data.get('light')
        geom_string = data.get('geom')
        if not forecast_io_key or not geom_string or (weather and light):
            return

        geom = json.loads(geom_string)
        coordinates = geom.get('coordinates')
        occurred_from = data['occurred_from']
        if not coordinates or not occurred_from:
            return

        params = {
            'base_url': 'https://api.forecast.io/forecast',
            'key': forecast_io_key,
            'lat': coordinates[1],
            'lon': coordinates[0],
            'time': occurred_from.replace(microsecond=0).isoformat(),
            'exclude': 'exclude=hourly,minutely,flags'
        }
        url = '{base_url}/{key}/{lat},{lon},{time}?{exclude}'.format(**params)
        response = requests.get(url)

        # Abort if the request failed for some reason
        if response.status_code is not requests.codes.ok:
            logger.warn("forecast.io query failed with url: {}".format(url))
            return

        response_dict = response.json()
        daily = response_dict.get('daily')
        currently = response_dict.get('currently')
        if not daily or not currently:
            return

        # Only set the weather if it's empty
        if not data.get('weather'):
            data['weather'] = currently.get('icon')

        daily_data = daily.get('data')
        if not daily_data or not len(daily_data):
            return

        forecast_data = daily_data[0]

        # Only set the light if it's empty
        if not data.get('light'):
            data['light'] = self.get_light_value(forecast_data, occurred_from)

    def get_light_value(self, forecast_data, occurred_from):
        """Helper for obtaining the light value using sunrise/sunset time

        :param forecast_data: Python dict representing data from forecast.io
        :param occurred_from: datetime object representing when the record occurred
        """
        # Selects from one of the following four values:
        #   day: occurred_from is between sunrise and sunset
        #   dawn: occurred_from is within the half-hour preceding sunrise
        #   dusk: occurred_from is within the half-hour following sunset
        #   night: occurred_from is not within day, dawn, or dusk
        #
        # Note: using a half-hour for dawn and dusk is just a rule-of-thumb, as
        # the actual definition involves angles of the sun in reference to the
        # horizon, and would be more complicated to properly implement.

        sunrise_time = forecast_data.get('sunriseTime')
        sunset_time = forecast_data.get('sunsetTime')
        if not sunrise_time or not sunset_time:
            return None

        tz = pytz.timezone(settings.TIME_ZONE)
        dawn_dusk_offset = datetime.timedelta(minutes=30)
        sunrise = tz.localize(datetime.datetime.fromtimestamp(sunrise_time))
        sunset = tz.localize(datetime.datetime.fromtimestamp(sunset_time))
        min_dawn = sunrise - dawn_dusk_offset
        max_dusk = sunset + dawn_dusk_offset

        if sunrise <= occurred_from <= sunset:
            return 'day'

        if min_dawn <= occurred_from <= sunrise:
            return 'dawn'

        if sunset <= occurred_from <= max_dusk:
            return 'dusk'

        return 'night'

    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields = ('uuid',)


class RecordTypeSerializer(ModelSerializer):

    current_schema = serializers.SerializerMethodField()

    class Meta:
        model = RecordType
        fields = '__all__'

    def get_current_schema(self, obj):
        current_schema = obj.get_current_schema()
        uuid = None
        if current_schema:
            uuid = str(current_schema.uuid)
        return uuid


class SchemaSerializer(ModelSerializer):
    """Base class for serializers of subclasses of models.SchemaModel"""
    schema = JsonSchemaField()


class RecordSchemaSerializer(SchemaSerializer):

    def create(self, validated_data):
        """Creates new schema or creates new version and updates next_version of previous"""
        if validated_data['version'] > 1:  # Viewset's get_serializer() will always add 'version'
            with transaction.atomic():
                current = RecordSchema.objects.get(record_type=validated_data['record_type'],
                                                   next_version=None)
                new = RecordSchema.objects.create(**validated_data)
                current.next_version = new
                current.save()
        elif validated_data['version'] == 1:  # New record_type
            new = RecordSchema.objects.create(**validated_data)
        else:
            raise serializers.ValidationError('Schema version could not be determined')
        return new

    class Meta:
        model = RecordSchema
        fields = '__all__'
        read_only_fields = ('uuid', 'next_version')


class BoundaryPolygonSerializer(GeoFeatureModelSerializer):

    data = JsonBField()

    class Meta:
        model = BoundaryPolygon
        geo_field = 'geom'
        id_field = 'uuid'
        exclude = ('boundary',)


class BoundaryPolygonNoGeomSerializer(ModelSerializer):
    """Serialize a BoundaryPolygon without any geometry info"""
    data = JsonBField()
    bbox = GeomBBoxField(source='geom')

    class Meta:
        model = BoundaryPolygon
        exclude = ('geom',)


class BoundarySerializer(GeoModelSerializer):

    label = serializers.CharField(max_length=128, allow_blank=False)
    color = serializers.CharField(max_length=64, required=False)
    display_field = serializers.CharField(max_length=10, allow_blank=True, required=False)
    data_fields = JsonBField(read_only=True, allow_null=True)
    errors = JsonBField(read_only=True, allow_null=True)

    def create(self, validated_data):
        boundary = super(BoundarySerializer, self).create(validated_data)
        boundary.load_shapefile()
        return boundary

    class Meta:
        model = Boundary
        # These meta read_only/exclude settings only apply to the fields the ModelSerializer
        # instantiates for you by default. If you override a field manually, you need to override
        # all settings there.
        # e.g. adding 'errors' to this tuple has no effect, since we manually define the errors
        # field above
        read_only_fields = ('uuid', 'status',)
        fields = '__all__'
