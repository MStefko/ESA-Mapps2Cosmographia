from __future__ import print_function
from datetime import datetime, timedelta, tzinfo


class UTC(tzinfo):
    """UTC"""
    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return UTC.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return UTC.ZERO


class MappsTime:
    """Time Utils"""
    mapps_pattern = '%Y-%m-%dT%H:%M:%S %Z'
    moc_pattern = '%Y-%m-%dT%H:%M:%S'

    def leap_seconds(self, date: datetime) -> int:
        leapsecond_dates = [
            datetime(1972, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1972, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1973, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1974, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1975, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1976, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1977, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1978, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1979, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1980, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1981, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1982, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1983, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1985, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1988, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1990, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1991, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1992, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1993, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1994, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1996, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(1997, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(1999, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(2006, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(2009, 1, 1, 0, 0, 0, 0, UTC()),
            datetime(2012, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(2015, 7, 1, 0, 0, 0, 0, UTC()),
            datetime(2017, 1, 1, 0, 0, 0, 0, UTC()),
        ]

        search = -1
        index = 0
        while index < len(leapsecond_dates) and leapsecond_dates[index] < date:
            search = index
            index += 1

        if search == -1:
            raise BaseException('Date too early')

        return 10 + search

    def __init__(self, mapps_utc_str: str):
        self.mapps_utc_str = mapps_utc_str[0:-1] + ' UTC'
        self.utc_tznoaware = datetime.strptime(self.mapps_utc_str, MappsTime.mapps_pattern)
        self.utc = datetime(self.utc_tznoaware.year, self.utc_tznoaware.month,
                            self.utc_tznoaware.day, self.utc_tznoaware.hour, self.utc_tznoaware.minute,
                            self.utc_tznoaware.second, tzinfo=UTC())
        self.tdb = self.utc + timedelta(seconds=32 + self.leap_seconds(self.utc), milliseconds=184)

    def utc_str(self) -> str:
        return self.utc.strftime(MappsTime.mapps_pattern)

    def tdb_str(self) -> str:
        return self.tdb.strftime(MappsTime.moc_pattern)

    def utc_tz_aware(self, utc: datetime) -> datetime:
        return datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second, tzinfo=UTC())

    @staticmethod
    def from_datetime(dt: datetime) -> 'MappsTime':
        return MappsTime(dt.strftime(MappsTime.moc_pattern) + 'Z')

    @staticmethod
    def from_bepi(utc_str_ntz: str) -> 'MappsTime':
        return MappsTime(utc_str_ntz + 'Z')


if __name__ == '__main__':
    t = MappsTime('2013-02-13T00:00:00Z')
    print(t.utc_str())
    print(t.tdb_str())
    t = MappsTime('2016-02-13T00:00:00Z')
    print(t.utc_str())
    print(t.tdb_str())
    t = MappsTime('2017-02-13T00:00:00Z')
    print(t.utc_str())
    print(t.tdb_str())

    t = MappsTime('2018-02-13T00:00:00Z')
    print(t.utc_str())
    print(t.tdb_str())
    print(t.tdb2_str())

