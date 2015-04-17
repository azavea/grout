from shapely.geometry import mapping, shape
from shapely.wkt import dumps
from shapely.wkb import loads as loads_b

def geom_preprocessor(data=None,**kwargs):
    """ Convert geojson dict to EWKT string """
    if 'geo' in data:
        data['geo'] = 'SRID=4326;' + dumps(shape(data['geo']))
        # if using ashlar.ashlar.geometries.Point
        # data['geo'] = dumps(shape(data['geo']))

def geom_patch_preprocessor(instance_id=None, data=None, **kwargs):
    """ Wrapper to handle extran instance_id param """
    return geom_preprocessor(data, **kwargs)

def geom_postprocessor(result=None, **kwargs):
    """ Convery WKBElement to geojson dict """
    if 'geo' in result:
        result['geo'] = mapping(loads_b(str(result['geo']).decode('hex')))
        # if using ashlar.ashlar.geometries.Point
        # result['geo'] = mapping(loads(str(result['geo'])))

def geom_many_postprocessor(result=None, search_params=None, **kwargs):
    """ Loop object results and process each geo item individually """
    for item in result['objects']:
        geom_postprocessor(item)