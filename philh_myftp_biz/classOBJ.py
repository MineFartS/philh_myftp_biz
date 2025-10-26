from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from .db import colors

class child:

    def __init__(self, parent, name:str):
        
        self.parent = parent
        self.name = name

        self.private = name.startswith('__')

        self.callable = callable(self.value())

        self.empty = (self.value() == None)

    def value(self):
        return getattr(self.parent, self.name)
    
    def __str__(self) -> str:
        from json import dumps

        try:
            return dumps(
                obj = self.value(),
                indent = 2
            )
        except:
            return str(self.value())

def path(obj) -> str:
    return obj.__class__.__module__ + '.' + obj.__class__.__qualname__

def children(obj) -> Generator['child']:
    for name in dir(obj):
        yield child(obj, name)

def stringify(obj) -> str:

    from io import StringIO
    
    IO = StringIO()

    IO.write('--- ')
    IO.write(path(obj))
    IO.write(' ---\n')

    for c in children(obj):
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
    from .pc import print as __print
    
    print()

    __print(
        stringify(obj),
        color = color
    )
    
    print()

def to_json(obj):

    json_obj = {}

    for c in children(obj):
        if not (c.private or c.callable or c.empty):
            json_obj[c.name] = c.value()

    return json_obj
