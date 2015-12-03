#!/usr/bin/python3

import ephem
import json
import celestrakdb

import satellite

CONFIG_FILENAME = '/Users/bjmclaug/source/stem_station/satellites.json'


def load_configuration(config_file):
    with open(CONFIG_FILENAME) as config_db:
        config = json.load(config_db)

    datasets = list(set([s['tle_dataset'] for s in config['satellites']]))
    sat_names = list(set([s['name'] for s in config['satellites']]))
    tle_db = celestrakdb.Celestrak(datasets, sat_names)
    ground_station = ephem.Observer()
    ground_station.lat = config['ground_station']['lat']
    ground_station.lon = config['ground_station']['lon']
    ground_station.elevation = config['ground_station']['elevation']
    ground_station.pressure = 0

    return [satellite.Satellite(
                  s['name'],
                  s['tx_frequency'],
                  s['tx_type'],
                  tle_db,
                  ground_station)
            for s in config['satellites']]

if __name__ == '__main__':

    satellites = load_configuration(CONFIG_FILENAME)

    for s in satellites:
        print(s.next_pass(45))
