from sqlalchemy.types import UserDefinedType
from sqlalchemy.sql import expression, func
import binascii

# Totally jacked from here:
# https://github.com/zzzeek/sqlalchemy/blob/c5edbc6fdc611d3c812735d83fe056fbb7d113f5/examples/postgis/postgis.py
#
# Mostly interchangeable with geoalchemy.objects.Geometry
# NOTE: Currently unused, but was left here in case it is easier to define our
# own filter functions via comparator_factory for filter parameters
#
# If used, should change the relevant lines in ashlar.api.serializers

# Python datatypes

class GisElement(object):
    """Represents a geometry value."""

    def __str__(self):
        return self.desc

    def __repr__(self):
        return "<%s at 0x%x; %r>" % (self.__class__.__name__,
                                    id(self), self.desc)

class BinaryGisElement(GisElement, expression.Function):
    """Represents a Geometry value expressed as binary."""

    def __init__(self, data):
        self.data = data
        expression.Function.__init__(self, "ST_GeomFromEWKB", data,
                                    type_=Geometry(coerce_="binary"))

    @property
    def desc(self):
        return self.as_hex

    @property
    def as_hex(self):
        return binascii.hexlify(self.data)

class TextualGisElement(GisElement, expression.Function):
    """Represents a Geometry value expressed as text."""

    def __init__(self, desc, srid=-1):
        self.desc = desc
        expression.Function.__init__(self, "ST_GeomFromText", desc, srid,
                                    type_=Geometry)


# SQL datatypes.

class Geometry(UserDefinedType):
    """Base PostGIS Geometry column type."""

    name = "GEOMETRY"

    def __init__(self, dimension=None, srid=-1,
                coerce_="text"):
        self.dimension = dimension
        self.srid = srid
        self.coerce = coerce_

    class comparator_factory(UserDefinedType.Comparator):
        """Define custom operations for geometry types."""

        # override the __eq__() operator
        def __eq__(self, other):
            return self.op('~=')(other)

        # add a custom operator
        def intersects(self, other):
            return self.op('&&')(other)

        # any number of GIS operators can be overridden/added here
        # using the techniques above.

    def _coerce_compared_value(self, op, value):
        return self

    def get_col_spec(self):
        return self.name

    def bind_expression(self, bindvalue):
        if self.coerce == "text":
            return TextualGisElement(bindvalue, srid=self.srid)
        elif self.coerce == "binary":
            return BinaryGisElement(bindvalue, srid=self.srid)
        else:
            assert False

    def column_expression(self, col):
        if self.coerce == "text":
            return func.ST_AsText(col, type_=self)
        elif self.coerce == "binary":
            return func.ST_AsBinary(col, type_=self)
        else:
            assert False

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, GisElement):
                return value.desc
            else:
                return value
        return process

    def result_processor(self, dialect, coltype):
        if self.coerce == "text":
            fac = TextualGisElement
        elif self.coerce == "binary":
            fac = BinaryGisElement
        else:
            assert False
        def process(value):
            if value is not None:
                return fac(value)
            else:
                return value
        return process

    def adapt(self, impltype):
        return impltype(dimension=self.dimension,
                srid=self.srid, coerce_=self.coerce)

# other datatypes can be added as needed.

class Point(Geometry):
    name = 'POINT'