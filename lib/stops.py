from collections import deque
import numpy as np
from .redis import red


class Cluster:

    def __init__(self):
        self.id = ''
        self.members = []

    def add_recursive(self, stop):
        queue = deque([stop])

        while len(queue):
            stop = queue.popleft()

            if stop.has_cluster(): continue

            if len(self.members) == 0:
                self.id = stop.id

            self.members.append(stop)
            stop.set_cluster(self.id)

            for stop in stop.get_near():
                if not stop.has_cluster():
                    queue.append(stop)

    def get_center(self):
        lons = list(map(
            lambda x: x.lon,
            self.members
        ))
        lats = list(map(
            lambda x: x.lat,
            self.members
        ))

        feature = {
            'type': 'Feature',
            'properties': {
                'id': self.id,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [np.mean(lons), np.mean(lats)],
            },
        }

        return feature

    @classmethod
    def from_id(cls, cluster_id):
        pass


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

    cluster = None

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
            lambda x: Stop.from_id(x),
            red.georadius('transport:stops:geohash', self.lon, self.lat, 50,
                unit='m',
            )
        ))

    def set_cluster(self, cluster_id):
        self.cluster = cluster_id
        red.set('transport:stops:{}:cluster'.format(self.id), self.cluster)

    def get_cluster(self):
        cluster_id = self.has_cluster()

        if cluster_id:
            return Cluster.from_id(cluster_id)
        else:
            cluster = Cluster()

            cluster.add_recursive(self)

            return cluster

    def has_cluster(self):
        cluster_id = red.get('transport:stops:{}:cluster'.format(self.id))

        if cluster_id:
            return cluster_id.decode('utf8')
        else: return None

    def persist(self):
        for attr, trans in self.attributes.items():
            red.set(self.redis_prefix(self.id, attr), getattr(self, attr))

        red.geoadd('transport:stops:geohash', self.lon, self.lat, self.id)

        red.set(self.redis_prefix(self.id, 'lat'), self.lat)
        red.set(self.redis_prefix(self.id, 'lon'), self.lon)

        return self

    @classmethod
    def from_key(cls, key):
        stop_id = red.get(key.decode('utf8')).decode('utf8')

        return cls.from_id(stop_id)

    @classmethod
    def from_id(cls, stop_id):
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
            'properties': {
                'route_id': self.route_id,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lon, self.lat],
            },
        }

        return feature

    @classmethod
    def get_stops(cls):
        result = []

        for key in red.keys('transport:stops:*:id'):
            stop = cls.from_key(key)

            if not stop.has_cluster():
                cluster = stop.get_cluster()

                result.append(cluster.get_center())

        return result
