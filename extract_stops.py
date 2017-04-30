#!/usr/bin/env python3
"""
This script will search for stops/ directories and extract all the available
stops considering possible duplicates
"""
import os
import json
import redis
import logging

red = redis.StrictRedis(host='localhost', port=6379, db=0)

def has_route(contents):
    return 'route.geojson' in contents

def get_stops():
    return [Stop.from_key(key).to_geojson() for key in red.keys('transport:stops:*:id')]


class Stop:
    tablename = 'stops'

    attributes = {
        'id'             : 'id',
        'route_id'       : 'routeId',
        'sequence'       : 'sequence',
        'travel_time'    : 'travelTime',
        'dwell_time'     : 'dwellTime',
        'arrival_time'   : 'arrivalTim',
        'departure_time' : 'departureT',
        'passenger_a'    : 'passengerA',
        'passenger_b'    : 'passengerB',
    }

    def __init__(self, data):
        for attr, trans in self.attributes.items():
            setattr(self, attr, data['properties'][trans])

        self.lat = data['geometry']['coordinates'][1]
        self.lon = data['geometry']['coordinates'][0]

    @classmethod
    def redis_prefix(cls, id, attr):
        return 'transport:{table}:{id}:{attr}'.format(
            table = cls.tablename,
            id    = id,
            attr  = attr,
        )

    def get_near(self):
        return list(map(
            lambda x:x[1],
            red.georadius('transport:stops:geohash', self.lon, self.lat, 20,
                unit='m',
                withdist=True,
                sort='DESC'
            )
        ))

    def persist(self):
        near_stops = self.get_near()

        for attr, trans in self.attributes.items():
            red.set(self.redis_prefix(self.id, attr), getattr(self, attr))

        red.geoadd('transport:stops:geohash', self.lon, self.lat, self.id)

        red.set(self.redis_prefix(self.id, 'lat'), self.lat)
        red.set(self.redis_prefix(self.id, 'lon'), self.lon)

        return self

    @classmethod
    def from_key(cls, key):
        stop_id = red.get(key.decode('utf8')).decode('utf8')

        return cls({
            'properties': {
                trans: red.get(cls.redis_prefix(stop_id, attr)).decode('utf8')
                for attr, trans in cls.attributes.items()
            },
            'geometry': {
                'coordinates': [
                    float(red.get(cls.redis_prefix(stop_id, 'lon')).decode('utf8')),
                    float(red.get(cls.redis_prefix(stop_id, 'lat')).decode('utf8')),
                ],
            },
        })

    def to_geojson(self):
        properties = {
            attr: getattr(self, attr) for attr, trans in self.attributes.items()
        }

        feature = {
            'type' : 'Feature',
            'properties': dict(),
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lon, self.lat],
            },
        }

        return feature


if __name__ == '__main__':
    for parent, dirs, files in os.walk('data'):
        if has_route(files) and parent.endswith('stops'):
            data = json.load(open(os.path.join(parent, 'route.geojson'), 'r'))

            for stopdata in data['features']:
                Stop(stopdata).persist()

    feature_collection = {
        'type': 'FeatureCollection',
        'features': get_stops(),
    }

    json.dump(feature_collection, open('data/stops.json', 'w'), indent=2)
