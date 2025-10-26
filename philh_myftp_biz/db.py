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
    """
    Type hint for keys in size.conv_factors
    """

    conv_factors = {
        'B' : 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    """
    Conversion Factors for file sizes

    EXAMPLE:
    size.conv_factors['B'] -> 1
    size.conv_factors['KB'] -> 1024
    """

    def to_bytes(string:str) -> int:
        """
        Convert Size String to bytes

        EXAMPLE:
        size.to_bytes('10B') -> 10
        size.to_bytes('10GB')
        """
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
    ) -> str:
        """
        Get Size String from bytes

        If unit is not given, then the unit will be automatically determined
        """

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
    """
    Type hint for keys in colors.values
    """

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
    r"""
    COLOR CONVERSION TABLE

    EXAMPLE:
    colors.values['RED'] -> '\033[31m'
    """

class Ring:
    """
    RING
    (Wrapper for keyring)
    """
    
    def __init__(self, name:str):
        from .text import hex

        self.name = 'philh.myftp.biz/' + hex.encode(name)

    def Key(self, name:str, default=None) -> 'Key':
        """
        Get Key in Ring by name
        """
        return Key(self, name)

class Key[T]:
    """
    KEY
    (Wrapper for keyring)
    """
    
    def __init__(self,
        ring: Ring,
        name: str,
        default = None
    ):
        from .text import hex
        
        self.ring = ring
        self.name = hex.encode(name)
        self.__default = default

    def save(self, value:T):
        """
        Save value to Key

        Saves as hexadecimal, so all pickleable objects are supported
        """
        from .text import hex
        from keyring import set_password

        set_password(
            service_name = self.ring.name,
            username = self.name,
            password = hex.encode(value)            
        )
        
    def read(self) -> T:
        """
        Read value from key
        """
        from .text import hex
        from keyring import get_password

        rvalue = get_password(
            service_name = self.ring.name,
            username = self.name
        )
        
        try:
            return hex.decode(rvalue)
        except TypeError:
            return self.__default