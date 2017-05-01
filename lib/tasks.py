import os
import json
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
                self.extract_in_place(zipfile, parent)

    def extract_in_place(zipfile, parent):
        dirname = os.path.join(parent, extract_name(zipfile))
        zipname = os.path.join(parent, zipfile)

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        subprocess.run('unzip {} -d {}'.format(zipname, dirname).split(' '))


class ConvertTask(Task):

    def convert(shapefile, parent):
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
