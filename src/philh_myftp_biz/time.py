import sys, time, math, datetime as dt


def every(s:int, n:int=sys.maxsize):
    for _ in range(n):
        time.sleep(s)
        yield

def toHMS(stamp):
    m, s = divmod(stamp, 60)
    h, m = divmod(m, 60)
    return ':'.join([
        strDigit(h),
        strDigit(m),
        strDigit(s)
    ])

def strDigit(n):
    return str( math.trunc(n) ).ljust( 2, '0' )

class Stopwatch:

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.running = False
        self.now = time.perf_counter

    def elapsed(self, string:bool=False):
        if self.running:
            elapsed = self.now() - self.start_time
        else:
            elapsed = self.end_time - self.start_time

        if string:
            return toHMS(elapsed)
        else:
            return elapsed

    def start(self):
        self.start_time = self.now()
        self.end_time = None
        self.running = True
        return self

    def stop(self):
        self.end_time = self.now()
        self.running = False
        return self

class from_stamp:

    tzinfo = dt.timezone(
        offset = dt.timedelta(hours=-4)
    )

    def __init__(self, stamp):
            
        self.dt = dt.datetime.fromtimestamp(stamp, tz=self.tzinfo)

        self.year = self.dt.year
        self.month = self.dt.month
        self.day = self.dt.day
        self.hour = self.dt.hour
        self.minute = self.dt.minute
        self.second = self.dt.second

        self.unix = stamp

        self.__unix__ = stamp

    def update(self):
        if self.__unix__ == self.unix:

            t = dt.datetime(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second
            )

            self.unix = t.timestamp()
            self.__unix__ = t.timestamp()

        else:
            t = dt.datetime.fromtimestamp(self.unix)

            self.year = t.year
            self.month = t.month
            self.day = t.day
            self.hour = t.hour
            self.minute = t.minute
            self.second = t.second
    
    def toString(self):
        class self_:
            None

        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, (int, float)):
                setattr(self_, name, str(value))

        return self_

    def stamp(self, format):
        return self.dt.strftime(format)

def interval(seconds):
    h, m, s = time.now().hms
    now = (h * 3600) + (m * 60) + s

    if (now == 0) and (seconds == 86400):
        return True
    else:
        return (now / seconds) == int(now / seconds)
    
def now():
    return from_stamp(time.time())

def from_string(string, separator='/', order='YMD'):

    split = string.split(separator)

    order = order.lower()
    Y = split[order.index('y')]
    M = split[order.index('m')]
    D = split[order.index('d')]

    dt_ = dt.datetime.strptime(f'{Y}-{M}-{D}', "%Y-%m-%d")
    return from_stamp(dt_.timestamp())

def get(*input):
    return from_stamp(dt.datetime(*input).timestamp())
