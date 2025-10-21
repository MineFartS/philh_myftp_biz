from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    import sys

# TODO
mime_types = {}

class size:

    units = Literal[
        'B',
        'KB',
        'MB',
        'GB',
        'TB'
    ]

    conv_factors = {
        'B' : 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }

    def to_bytes(string:str):
        from re import search

        match = search(
            r"(\d+(\.\d+)?)\s*([a-zA-Z]+)",
            string.strip()
        )

        value = float(match.group(1))

        unit = match.group(3).upper()
        unit = unit[0] + unit[-1]

        return value * size.conv_factors[unit]

    def from_bytes(
        value: int | float,
        unit: units | None = None,
        ndigits: int = 'sys.maxsize'
    ):

        format = lambda unit: round(
            number = (float(value) / size.conv_factors[unit]),
            ndigits = ndigits
        )

        if unit:
            return str(format(unit)) + ' ' + unit
        else:
            r = 0
            for unit in reversed(size.conv_factors):
                r = format(unit)
                if r >= 1:            
                    return str(r) + ' ' + unit

class colors:

    names = Literal[
        'BLACK',
        'RED',
        'GREEN',
        'YELLOW',
        'BLUE',
        'MAGENTA',
        'CYAN',
        'WHITE',
        'DEFAULT'
    ]

    values = {
        'BLACK' : '\033[30m',
        'RED' : '\033[31m',
        'GREEN' : '\033[32m',
        'YELLOW' : '\033[33m',
        'BLUE' : '\033[34m',
        'MAGENTA' : '\033[35m',
        'CYAN' : '\033[36m',
        'WHITE' : '\033[37m',
        'DEFAULT' : '\033[0m'
    }

class Ring:
    
    def __init__(self, name:str):
        from .text import hex

        self.name = 'philh.myftp.biz/' + hex.encode(name)

    def Key(self, name:str, default=None):
        return Key(self, name)

class Key[T]:
    
    def __init__(self, ring:Ring, name:str, default=None):
        from .text import hex
        
        self.ring = ring
        self.name = hex.encode(name)
        self.default = default

    def save(self, value:T):
        from .text import hex
        from keyring import set_password

        set_password(
            service_name = self.ring.name,
            username = self.name,
            password = hex.encode(value)            
            )
        
    def read(self) -> T:
        from .text import hex
        from keyring import get_password

        rvalue = get_password(
            service_name = self.ring.name,
            username = self.name
            )
        
        try:
            return hex.decode(rvalue)
        except TypeError:
            return self.default