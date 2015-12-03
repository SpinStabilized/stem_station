'''
.. module:: satellite
   :platform: Unix, OS X, Windows
   :synopsis: Satellite data objects.

.. moduleauthor:: Brian McLaughlin <bjmclaughlin@gmail.com>

'''
import math
import ephem

C = 299792458


class Satellite(object):
    '''Satellite data object'''

    def __init__(self, name, tx_frequency=0.0, tx_type=None, tle_db=None,
                 ground_station=None):
        self.name = name
        self.tx_frequency = tx_frequency
        self.tx_type = tx_type
        self.tle_from_db(tle_db)
        self.ground_station = ground_station

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def tx_frequency(self):
        return self._tx_frequency

    @tx_frequency.setter
    def tx_frequency(self, value):
        self._tx_frequency = value

    @property
    def tx_type(self):
        return self._tx_type

    @tx_type.setter
    def tx_type(self, value):
        self._tx_type = value

    @property
    def rx_frequency(self):
        return self.tx_frequency + -self.doppler_shift

    @property
    def ephemeris(self):
        return self._ephemeris

    @property
    def tle(self):
        return self._tle

    @tle.setter
    def tle(self, value):
        self._tle = value
        self._ephemeris = ephem.readtle(self.name,
                                        self.tle.tle1,
                                        self.tle.tle2)

    @property
    def ground_station(self):
        return self._ground_station

    @ground_station.setter
    def ground_station(self, value):
        self._ground_station = value

    def tle_from_db(self, tle_db):
        if not tle_db:
            self.tle = None
        else:
            tle_objs = [tle for tle in tle_db.tle if tle.name == self.name]
            if not tle_objs:
                self.tle = None
            else:
                self.tle = tle_objs[0]

    @property
    def doppler_shift(self):
        self.ephemeris.compute(self.ground_station)
        return (self.ephemeris.range_velocity / C) * self.tx_frequency

    def next_pass(self, min_elev=0):
        pass_found = False
        a_pass = None
        date_save = self.ground_station.date
        while not pass_found:
            a_pass = self.ground_station.next_pass(self.ephemeris)
            max_elev = math.degrees(a_pass[3])
            if max_elev <= min_elev:
                self.ground_station.date = a_pass[4] + ephem.minute
            else:
                pass_found = True

        self.ground_station.date = date_save
        return {'AOS': a_pass[0],
                'R_AZ': math.degrees(a_pass[1]),
                'PEAK': a_pass[2],
                'MAX_EL': math.degrees(a_pass[3]),
                'LOS': a_pass[4],
                'S_AZ': math.degrees(a_pass[5])
                }
