#!/usr/bin/env python3
import requests
import os
import subprocess

def has_shape(contents):
    return any(map(
        lambda x: x.endswith('.shp'),
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
    for parent, nose, contents in os.walk('data'):
        if has_shape(contents) and len(contents) == 4:
            shapefile = get_shape(contents)

            convert(shapefile, parent)