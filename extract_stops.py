#!/usr/bin/env python3
"""
This script will search for stops/ directories and extract all the available
stops considering possible duplicates
"""
import os
import json

def has_route(contents):
    return 'route.geojson' in contents

def add_stop(stop):
    pass

def get_stops():
    return []

if __name__ == '__main__':
    for parent, dirs, files in os.walk('data'):
        if has_route(files) and parent.endswith('stops'):
            data = json.load(open(os.path.join(parent, 'route.geojson'), 'r'))

            for stop in data['features']:
                add_stop(stop)

    json.dump(get_stops(), open('data/stops.json', 'w'), indent=2)
