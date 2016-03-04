import celestrakdb
import ephem

def main():
    satellites = ['NOAA 15', 'NOAA 18', 'NOAA 19']
    tle_db = celestrakdb.Celestrak(['noaa'], satellites)


if __name__ == '__main__':
    main()
