from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import colors

class attr:

    def __init__(self, parent, name:str):
        
        self.parent = parent
        self.name = name

        self.private = name.startswith('__')

        self.callable = callable(self.value())

        self.empty = (self.value() == None)

    def value(self):
        return getattr(self.parent, self.name)
    
    def __str__(self):
        try:
            return json.dumps(
                obj = self.value(),
                indent = 2
            )
        except:
            return str(self.value())

def attrs(obj):
    for name in dir(obj):
        yield attr(obj, name)

def path(obj) -> str:
    """
    Get Full path of instance

    Ex: path(print) -> '__builtins__.print'
    """
    return obj.__class__.__module__ + '.' + obj.__class__.__qualname__

def stringify(obj) -> str:
    """
    Creates a string containing a table of all attributes of an instance
    (for debugging)
    """
    from io import StringIO
    
    IO = StringIO()

    IO.write('--- ')
    IO.write(path(obj))
    IO.write(' ---\n')

    for c in attrs(obj):
        if not (c.private or c.callable or c.empty):
            IO.write(c.name)
            IO.write(' = ')
            IO.write(str(c))
            IO.write('\n')

    return IO.getvalue()

def log(
    obj,
    color: 'colors.names' = 'DEFAULT'
) -> None:
    """
    Print all attributes of the instance to the terminal
    """
    from .pc import print as __print
    
    print()

    __print(
        stringify(obj),
        color = color
    )
    
    print()

def to_json(obj) -> dict:
    """
    Convert an instance to a dictionary
    """

    json_obj = {}

    dir(obj)

    for c in attrs(obj):
        if not (c.private or c.callable or c.empty):
            json_obj[c.name] = c.value()

    return json_obj
