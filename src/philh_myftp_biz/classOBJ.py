from . import pc

import json

class new:
    def __init__(self, **args):
        for name in args:
            setattr(self, name, args[name])

def path(obj):
    return obj.__class__.__module__ + '.' + obj.__class__.__qualname__

def values(obj):

    types = (int, float, str, bool, list, tuple, map, dict)

    for name in dir(obj):

        value = getattr(obj, name)

        is_type = isinstance(value, types)
        not_hidden = not name.startswith('_')

        if is_type and not_hidden:
            yield name, value

def log(obj, color:pc.print.colors='DEFAULT'):

    print()

    pc.print(
        '--- ' + path(obj) + ' ---',
        color = color
    )

    for name, value in values(obj):

        try:
            text = json.dumps(value, indent=4)
        except:
            text = path(value)

        pc.print(
            name + ' = ' + text,
            color = color
        )

    print()
