#!/usr/bin/env python3
import os
import subprocess

def has_shape(contents):
    return any(map(
        lambda x: x.endswith('.shp'),
        contents
    ))

def doesnt_have_json(contents):
    return not any(map(
        lambda x: x.endswith('.geojson'),
        contents
    ))

def get_shape(contents):
    return list(filter(
        lambda x: x.endswith('.shp'),
        contents
    ))[0]

def convert(shapefile, parent):
    shapename = os.path.join(parent, shapefile)
    geojsonname = os.path.join(parent, 'route.geojson')

    subprocess.run('ogr2ogr -f geoJSON {} {}'.format(geojsonname, shapename).split(' '))

if __name__ == '__main__':
    for parent, dirs, contents in os.walk('data'):
        if has_shape(contents) and doesnt_have_json(contents):
            shapefile = get_shape(contents)

            convert(shapefile, parent)
