'''
Objects for intereacting with the `Celestrak <http://celestrak.com/>`_
online database.

This module provides two objects for easy collection of data on satellite Two
Line Elements (TLE) from the `Celestrak <http://celestrak.com/>`_ database. The
data in a TLE provides all of the information necessary to determine a
satellite's orbit properties. A TLE is actually three lines with the first
line containing the satellite name. The remaining two lines contain other
identifying information and the orbital parameters.

The functions provided in this module do not parse this TLE data, only provides
a retrival from the online database and easy access to the lines for processing
in other contexts.

Classes
-------
- `Celestrak` -- An object that stores the requested satellite TLE items
- `TLEItem` -- An object that stores individual TLE information

'''

import urllib.request
import re
from datetime import datetime


class Celestrak(object):
    '''Object to interface with TLE raw datafiles.

    This is the main object for retrieving the TLE files and storing the
    requested TLE objects.

    Parameters
    ----------
    dataset : list of strings, optional
        A list of datasets to use in searching for a specific satellite. Useful
        if the satellite dataset is already known. To search all known datasets
        leave the parameter out or provide an empty list. For example,
        ```['amateur', 'noaa']```.
    satellites : list of strings, optional
        A list of specific satellites to find by name such as
        ```['NOAA 18', 'NOAA 19']```.

    Properties
    ----------
    dataset : list of strings
        The list of datasets to search. This allows for a retrieval of the
        datasets being used in the search as well as updating the datasets
        searched. Note - If the datasets are changed, run the ``update_tle()``
        method to update the TLE data.

    '''

    '''The base URL for the Celestrak datasets.'''
    base_url = 'http://www.celestrak.com/NORAD/elements/'

    '''The list of known datasets hosted on Celestrak.'''
    datasets = ['amateur',
                'argos',
                'beidou',
                'cubesat',
                'dmc',
                'education',
                'engineering',
                'galileo',
                'geo',
                'geodetic',
                'glo-ops',
                'globalstar',
                'goes',
                'gorizont',
                'gps-ops',
                'intelsat',
                'iridium',
                'military',
                'molniya',
                'musson',
                'nnss',
                'noaa',
                'orbcomm',
                'other',
                'other-comm',
                'radar',
                'raduga',
                'resource',
                'sarsat',
                'sbas',
                'science',
                'stations',
                'tdrss',
                'tle-new',
                'visual',
                'weather',
                'x-comm',
                '1999-025',
                'iridium-33-debris',
                'cosmos-2251-debris',
                '2012-044']

    '''Encoding for the Celestrak data files.'''
    dataset_encoding = 'ASCII'

    '''Number of text lines per TLE object.'''
    lines_per_object = 3

    '''Define the TLE input file line-ending.'''
    tle_file_line_ending = '\r\n'

    def __init__(self, dataset=[], satellites=[]):
        '''Celetrak DB object.

        :param dataset: datasets to use. See :func:`Celestrak.dataset`
        :type dataset:  :class:`list`
        :param satellites: Satellite names. See :func:`Celestrak.satellites`
        :type satellites: :class:`list`

        '''

        if not dataset:
            self.dataset = self.datasets
        else:
            self.dataset = dataset

        self.satellites = satellites
        self._tle = []
        self.last_update = None

        self.update_tle()

    @property
    def dataset(self):
        '''
        The list of datasets defined at initilization.

        :getter: Returns a list of dataset names
        :setter: Set the list of datasets
        :type: list
        '''
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value

    @property
    def satellites(self):
        '''
        The list of satellites to filter on.

        :getter: Returns the list of satellites
        :setter: Set the list of satellites
        :type: list
        '''
        return self._satellites

    @satellites.setter
    def satellites(self, value):
        self._satellites = value

    @property
    def tle(self):
        '''
        The list of :class:`TLEItems` as retrieved based on :attr:`dataset` &
        :attr:`satellites`.
        '''
        return self._tle

    @property
    def last_update(self):
        '''
        The last time the list was refreshed.

        :getter: Returns the last time the data was refreshed from the sources.
        :type: :class:`datetime.datetime`
        '''
        return self._last_update

    @last_update.setter
    def last_update(self, value):
        self._last_update = value

    @property
    def age(self):
        '''
        The amount of time since the TLE data was refresed from the sources.

        :getter: The amound of time since the TLE data was refreshed
        :type: :class:`datetime.timedelta`
        '''
        age = None
        if self.last_update is not None:
            age = datetime.utcnow() - self._last_update

        return age

    def update_tle(self):
        '''
        Retrieve the TLE data from the source and update the database.

        .. note::
           Also updates the time of the data refresh.


        '''
        self._tle = []
        for data in self.dataset:

            # Format the URL for the dataset to retrieve
            url = '{}{}.txt'.format(self.base_url, data)
            tle_raw = None

            try:
                # retireve the ephemeris file data
                with urllib.request.urlopen(url) as ephemeris_file:
                    tle_raw = ephemeris_file.read().decode(
                        self.dataset_encoding).split(self.tle_file_line_ending)

            except urllib.request.URLError:
                pass  # TODO: Add better error handling

            # check for and remove any extra lines at the end
            tle_raw = tle_raw[:(len(tle_raw) -
                                (len(tle_raw) % self.lines_per_object))]

            # break the tle data into 3 line groups & create TLEItem Objects
            self._tle.extend([TLEItem(tle_raw[index].strip(),
                                      tle_raw[index+1],
                                      tle_raw[index+2],
                                      dataset=data)
                             for index in list(range(0, len(tle_raw), 3))])

        # If we received a list of satellites, filter on that set
        if self.satellites:
            self._tle = [tle_item for tle_item in self.tle
                         if (tle_item.name in self.satellites) or
                            (tle_item.alt in self.satellites) or
                            (tle_item.raw_name in self.satellites)]

        self._last_update = datetime.utcnow()

    def tle_file_output(output_file):
        '''Generate a TLE file from the tle database.'''
        pass  # TODO Implement this method


class TLEItem(object):
    NAME_REGEX = '^(?P<name>[\w\- ]+)(?P<alt>\(.+\))?(?P<status>\[.\])?'

    STATUS_MAPPING = {'+': 'operational',
                      'P': 'partially_operational',
                      'S': 'spare',
                      '-': 'non-operational',
                      'B': 'backup_standby',
                      'X': 'extended_mission'}

    def __init__(self, line0, line1, line2, dataset=''):
        name_information = self.parse_raw_name(line0)
        self.raw_name = line0
        self.name = name_information['name']
        self.alt = name_information['alt']
        self.status = name_information['status']

        self.tle1 = line1
        self.tle2 = line2
        self.dataset = dataset

    @staticmethod
    def parse_raw_name(raw_name):
        name_information = {}

        # Special Case Name Handling
        if '&' in raw_name:
            name_list = raw_name.split('&')
            name_information['name'] = name_list[0].strip()
            name_information['alt'] = name_list[1].strip()
            name_information['status'] = ''

        else:
            name_information = re.match(
                                    TLEItem.NAME_REGEX, raw_name).groupdict()
            if not name_information['name']:
                name_information['name'] = ''
            else:
                name_information['name'] = name_information['name'].strip()

            if name_information['alt']:
                name_information['alt'] = name_information['alt'][1:-1]
            else:
                name_information['alt'] = ''

            if name_information['status']:
                name_information['status'] = name_information['status'][1:-1]
            else:
                name_information['status'] = ''

        return name_information

    @property
    def raw_name(self):
        return self._raw_name

    @raw_name.setter
    def raw_name(self, value):
        self._raw_name = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def alt(self):
        return self._alt

    @alt.setter
    def alt(self, value):
        self._alt = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def tle1(self):
        return self._tle1

    @tle1.setter
    def tle1(self, value):
        self._tle1 = value

    @property
    def tle2(self):
        return self._tle2

    @tle2.setter
    def tle2(self, value):
        self._tle2 = value

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value


if __name__ == '__main__':
    db = Celestrak(['amateur'])
    for sat in db.tle:
        print('Satellite: {} / Alternate Name: {}'.format(sat.name, sat.alt))
