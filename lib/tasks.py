import os
import json
import subprocess
from .stops import Stop
from .utils import *

class Task:

    def register(self, tasks):
        tasks[type(self).__name__[:-4].lower()] = self

    def on_process(self, parent, dirs, files): pass

    def on_finish(self): pass


class UncompressTask(Task):

    def on_process(self, parent, dirs, files):
        if has('.zip', files):
            for zipfile in files:
                if not os.path.isdir(os.path.join(parent, extract_name(zipfile))):
                    self.extract_in_place(zipfile, parent)

    def extract_in_place(self, zipfile, parent):
        dirname = os.path.join(parent, extract_name(zipfile))
        zipname = os.path.join(parent, zipfile)

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        subprocess.run('unzip {} -d {}'.format(zipname, dirname).split(' '))


class ConvertTask(Task):

    def convert(self, shapefile, parent):
        shapename = os.path.join(parent, shapefile)
        geojsonname = os.path.join(parent, 'route.geojson')

        subprocess.run('ogr2ogr -f geoJSON {} {}'.format(geojsonname, shapename).split(' '))

    def on_process(self, parent, dirs, files):
        if has('.shp', files) and hasnt('.geojson', files):
            shapefile = get('.shp', files)

            self.convert(shapefile, parent)


class ExtractStopsTask(Task):

    def on_process(self, parent, dirs, files):
        if has('.geojson', files) and parent.endswith('stops'):
            data = json.load(open(os.path.join(parent, 'route.geojson'), 'r'))

            for stopdata in data['features']:
                Stop(stopdata).persist()


class DumpStopsTask(Task):

    def on_finish(self):
        feature_collection = {
            'type': 'FeatureCollection',
            'features': Stop.get_stops(),
        }

        json.dump(feature_collection, open('build/stops.geojson', 'w'), indent=2)

class ComputeBoundsTask(Task):

    def __init__(self):
        self.max_lat = -float('inf')
        self.max_lon = -float('inf')
        self.min_lat = float('inf')
        self.min_lon = float('inf')

    def on_process(self, parent, dirs, files):
        if has('.geojson', files):
            geojsonname = get('.geojson', files)
            data = json.load(open(os.path.join(parent, geojsonname), 'r'))

            for feature in data['features']:
                if feature['geometry']['type'] == 'LineString':
                    for coordinate in feature['geometry']['coordinates']:
                        self.process_lon(coordinate[0])
                        self.process_lat(coordinate[1])

                if feature['geometry']['type'] == 'Point':
                    self.process_lon(feature['geometry']['coordinates'][0])
                    self.process_lat(feature['geometry']['coordinates'][1])

    def on_finish(self):
        print('({},{},{},{})'.format(self.min_lat, self.min_lon, self.max_lat, self.max_lon))

    def process_lat(self, lat):
        if lat > self.max_lat:
            self.max_lat = lat
        if lat < self.min_lat:
            self.min_lat = lat

    def process_lon(self, lon):
        if lon > self.max_lon:
            self.max_lon = lon
        if lon < self.min_lon:
            self.min_lon = lon
