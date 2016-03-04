'''
.. module:: celestrakdb
   :platform: Unix, OS X, Windows
   :synopsis: Interface for managing TLE data.

.. moduleauthor:: Brian McLaughlin <bjmclaughlin@gmail.com>

'''

import requests
import subprocess
import os
import re
from datetime import datetime, timedelta

from lxml import html

def get_dataset_list():
    # dataset_page = requests.get('http://www.celestrak.com/NORAD/elements/')
    dataset_page = requests.get(Celestrak.BASE_URL)
    page_tree = html.fromstring(dataset_page.content)
    dataset_files = page_tree.xpath('/html/body//a[contains(@href,"txt")]/@href')
    return [dataset.split('.')[0] for dataset in dataset_files]

class Celestrak(object):
    '''Object to interface with TLE raw datafiles.'''

    '''The base URL for the Celestrak datasets.'''
    BASE_URL = 'http://www.celestrak.com/NORAD/elements/'

    '''Encoding for the Celestrak data files.'''
    DATASET_ENCODING = 'ASCII'

    '''Number of text lines per TLE object.'''
    LINES_PER_OBJECT = 3

    '''Define the TLE input file line-ending.'''
    TLE_FILE_LINE_ENDING = '\r\n'

    def __init__(self, dataset=[], satellites=[]):
        '''Celetrak DB object.

        :param dataset: Celestrak datasets to use. See :func:`Celestrak.dataset`
        :type dataset:  :class:`list`
        :param satellites: Satellite names to filter on. See :func:`Celestrak.satellites`
        :type satellites: :class:`list`

        '''
        if not dataset:
            self.dataset = self.datasets()
        else:
            self.dataset = dataset

        self.satellites = satellites
        self._tle = []
        self.last_update = None

        self.update_tle()

    def datasets(self):
        '''Get the list of known datasets hosted on Celestrak.'''
        dataset_page = requests.get(self.BASE_URL)
        page_tree = html.fromstring(dataset_page.content)
        dataset_files = page_tree.xpath('/html/body//a[contains(@href,"txt")]/@href')
        return [dataset.split('.')[0] for dataset in dataset_files]

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
            url = '{}{}.txt'.format(self.BASE_URL, data)
            tle_raw = None

            ephemeris_file = requests.get(url)
            tle_raw = ephemeris_file.text.decode(
                    self.DATASET_ENCODING).split(self.TLE_FILE_LINE_ENDING)
            print tle_raw

            # check for and remove any extra lines at the end
            tle_raw = tle_raw[:(len(tle_raw) -
                                (len(tle_raw) % self.LINES_PER_OBJECT))]

            # break the tle data into 3 line groups & create TLEItem Objects
            self._tle.extend([TLEItem(tle_raw[index].strip(),
                                      tle_raw[index+1],
                                      tle_raw[index+2],
                                      dataset=data)
                                      for index in list(range(0,
                                                        len(tle_raw), 3))])

        # If we received a list of satellites, filter on that set
        if self.satellites:
            self._tle = [tle_item for tle_item in self.tle
                            if (tle_item.name in self.satellites) or
                               (tle_item.alt  in self.satellites) or
                               (tle_item.raw_name in self.satellites)]

        self._last_update = datetime.utcnow()

    def tle_file_output(output_file):
        '''Generate a TLE file from the tle database.'''
        pass  # TODO Implement this method


class TLEItem(object):
    NAME_REGEX = '^(?P<name>[\w\- ]+)(?P<alt>\(.+\))?(?P<status>\[.\])?'

    STATUS_MAPPING = {'+':'operational',
                      'P':'partially_operational',
                      'S':'spare',
                      '-':'non-operational',
                      'B':'backup_standby',
                      'X':'extended_mission'}

    def __init__(self, line0, line1, line2, dataset=''):
        name_information = self.parse_raw_name(line0)
        self.raw_name = line0
        self.name   = name_information['name']
        self.alt    = name_information['alt']
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
            name_information['alt']  = name_list[1].strip()
            name_information['status'] = ''

        else:
            name_information = re.match(TLEItem.NAME_REGEX, raw_name).groupdict()
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
    db = Celestrak(['noaa'])
    for sat in db.tle:
        print('Satellite: {} / Alternate Name: {}'.format(sat.name, sat.alt))
