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

    def __init__(self, data, redis):
        for attr, trans in self.attributes.items():
            setattr(self, attr, data['properties'][trans])

        self.lat = data['geometry']['coordinates'][1]
        self.lon = data['geometry']['coordinates'][0]

        self.redis = redis

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
            self.redis.georadius('transport:stops:geohash', self.lon, self.lat, 20,
                unit='m',
                withdist=True,
                sort='DESC'
            )
        ))

    def persist(self):
        near_stops = self.get_near()

        for attr, trans in self.attributes.items():
            self.redis.set(self.redis_prefix(self.id, attr), getattr(self, attr))

        self.redis.geoadd('transport:stops:geohash', self.lon, self.lat, self.id)

        self.redis.set(self.redis_prefix(self.id, 'lat'), self.lat)
        self.redis.set(self.redis_prefix(self.id, 'lon'), self.lon)

        return self

    @classmethod
    def from_key(cls, key, redis):
        stop_id = redis.get(key.decode('utf8')).decode('utf8')

        return cls({
            'properties': {
                trans: redis.get(cls.redis_prefix(stop_id, attr)).decode('utf8')
                for attr, trans in cls.attributes.items()
            },
            'geometry': {
                'coordinates': [
                    float(redis.get(cls.redis_prefix(stop_id, 'lon')).decode('utf8')),
                    float(redis.get(cls.redis_prefix(stop_id, 'lat')).decode('utf8')),
                ],
            },
        }, redis)

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

