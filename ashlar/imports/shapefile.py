import os
import tempfile
import zipfile
from django.contrib.gis.geos import MultiPolygon, Polygon


def extract_zip_to_temp_dir(filename):
    """Extracts zipfile into a new temporary folder."""
    temp_dir = tempfile.mkdtemp()
    unzipper = zipfile.ZipFile(filename)
    files_to_extract = [f for f in unzipper.namelist() if '__MACOSX' not in f]
    unzipper.extractall(temp_dir, files_to_extract)
    unzipper.close()

    return temp_dir


def get_shapefiles_in_dir(path):
    """Finds any shapefiles in path."""
    all_files = []
    for dirpath, subdirs, files in os.walk(path):
        for name in files:
            all_files.append(os.path.join(dirpath, name))
    shapefiles = [f for f in all_files if f.endswith('.shp')]
    return shapefiles


def make_multipolygon(geom):
    """Wraps Polygons in MultiPolygons"""
    if isinstance(geom.geos, Polygon):
        return MultiPolygon(geom.geos)
    elif isinstance(geom.geos, MultiPolygon):
        return geom.geos
    else:
        raise ValueError('Feature is not a MultiPolygon or Polygon')
