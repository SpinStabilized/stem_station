import celestrakdb
import ephem

def main():
    satellite_names = ['NOAA 15', 'NOAA 18', 'NOAA 19']
    tle_db = celestrakdb.Celestrak(['noaa'], satellite_names)

    satellites = [ephem.readtle(tle.name, tle.tle1, tle.tle2) for tle in tle_db.tle]
    print satellites



if __name__ == '__main__':
    main()
