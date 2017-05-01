#!/usr/bin/env python3
import argparse
from functools import wraps
import os
import subprocess
import redis
import json
from lib.stops import Stop

available_tasks = dict()

red = redis.StrictRedis(host='localhost', port=6379, db=0)

def task(func):
    available_tasks[func.__name__] = func
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def has(ending, files):
    return any(map(
        lambda x: x.endswith(ending),
        files
    ))

def hasnt(ending, files):
    return not any(map(
        lambda x: x.endswith(ending),
        files
    ))

def extract_in_place(zipfile, parent):
    dirname = os.path.join(parent, extract_name(zipfile))
    zipname = os.path.join(parent, zipfile)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    subprocess.run('unzip {} -d {}'.format(zipname, dirname).split(' '))

def extract_name(somefile):
    return '.'.join(somefile.split('.')[:-1])

def get(ending, files):
    return list(filter(
        lambda x: x.endswith(ending),
        files
    ))[0]

def convert(shapefile, parent):
    shapename = os.path.join(parent, shapefile)
    geojsonname = os.path.join(parent, 'route.geojson')

    subprocess.run('ogr2ogr -f geoJSON {} {}'.format(geojsonname, shapename).split(' '))

def get_stops():
    return [Stop.from_key(key, red).to_geojson() for key in red.keys('transport:stops:*:id')]

@task
def uncompress(parent, dirs, files):
    if has('.zip', files):
        for zipfile in files:
            extract_in_place(zipfile, parent)

@task
def convert(parent, dirs, files):
    if has('.shp', files) and hasnt('.geojson', files):
        shapefile = get('.shp', files)

        convert(shapefile, parent)

@task
def extract_stops(parent, dirs, files):
    if has('.geojson', files) and parent.endswith('stops'):
        data = json.load(open(os.path.join(parent, 'route.geojson'), 'r'))

        for stopdata in data['features']:
            Stop(stopdata, red).persist()

    feature_collection = {
        'type': 'FeatureCollection',
        'features': get_stops(),
    }

    json.dump(feature_collection, open('data/stops.json', 'w'), indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apply different administrative tasks to data')

    parser.add_argument('task', choices=available_tasks, help='the task to perform')

    args = parser.parse_args()

    for parent, dirs, files in os.walk('data'):
        available_tasks[args.task](parent, dirs, files)
