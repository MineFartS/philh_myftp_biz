from typing import Literal

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
