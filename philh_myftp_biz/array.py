from typing import Callable, Self, TYPE_CHECKING, Literal, List

if TYPE_CHECKING:
    from .file import JSON, PKL
    from .pc import _var

__max = max
__filter = filter

class new[_T]:
    """
    List/Tuple Wrapper

    Stores data to the local disk instead of memory
    """

    def __init__(self,
        array: 'list | tuple | Self | JSON | _var | PKL' = []
    ):
        from .file import JSON, PKL, temp
        from .pc import _var

        if isinstance(array, (JSON, _var, PKL)):
            self.var = array

        elif isinstance(array, new):
            self.var = array.var

        elif isinstance(array, (list, tuple)):
            self.var = PKL(
                temp('array', 'pkl')
            )
            self.var.save(list(array))

        self.save = self.var.save
        """Save data"""

        self.read = self.var.read
        """Read data"""

    def append(self, item:_T):
        self.save(
            self.read() + [item]
        )

    def remove(self, item):
        
        arr: list = self.read()

        if item in arr:
            arr.remove(item)
            self.save(arr)

    def rm_duplicates(self):
        data = self.read()
        data_ = []
        for item in data:
            if item not in data_:
                data_.append(item)
        self.save(data_)

    def __iter__(self):
        self._data:list = self.read()
        return self

    def __next__(self):
        if len(self._data) == 0:
            raise StopIteration
        else:
            value = self._data[0]
            self._data = self._data[1:]
            return value

    def __len__(self):
        return len(self.read())
    
    def __getitem__(self, key):
        return self.read()[key]

    def __setitem__(self, key, value):
        data = self.read()
        data[key] = value
        self.save(data)

    def __delitem__(self, key):
        self.remove(self.read()[key])

    def __iadd__(self, value):
        self.append(value)
        return self

    def __isub__(self, value):

        if isinstance(value, (list, tuple)):
            for item in value:
                self.remove(item)
        else:
            self.remove(value)

        return self

    def __contains__(self, value):
        return value in self.read()

    def sorted(self, func:Callable[[_T], Self]=lambda x: x) -> Self:
        data = sort(self.read(), func)
        return new(data)

    def sort(self, func:Callable[[_T], Self]=lambda x: x) -> None:
        self.save( self.sorted(func).read() )

    def max(self, func:Callable[[_T], Self]=lambda x: x) -> None | _T:
        if len(self) > 0:
            return max(self.read(), func)
    
    def filtered(self, func:Callable[[_T], Self]=lambda x: x) -> Self:
        data = filter(self.read(), func)
        return new(data)
    
    def filter(self, func:Callable[[_T], Self]=lambda x: x) -> None:
        self.save( filter(self.read(), func) )

    def random(self, n:int=1) -> Self:
        data = random.sample(self.read(), n)
        return new(data)

    def shuffle(self) -> None:
        self.save(self.shuffled().read())
    
    def shuffled(self) -> Self:
        return self.random(len(self.read()))

    def __str__(self):
        from json import dumps

        return dumps(self.read(), indent=2)

def stringify(array:list):
    for x, item in enumerate(array):
        array[x] = str(item)
    return array

def auto_convert(array:list):
    from .text import auto_convert

    array = array.copy()

    for x, a in enumerate(array):
        array[x] = auto_convert(a)

    return array

def generate(generator):
    return [x for x in generator]

def priority(_1:int, _2:int, reverse:bool=False):
    
    p = _1 + (_2 / (1000**1000))
    
    if reverse:
        p *= -1

    return p

class random:

    def sample(array:list, n:int=1):
        from random import sample

        if len(array) == 0:
            return None
        elif n > len(array):
            n = len(array)

        return sample(array, n)

    def choice(array:list):
        from random import choice

        if len(array) > 0:
            return choice(array)

def filter(array:list, func=lambda x: x):
    return list(__filter(func, array))

def sort(array:list, func=lambda x: x):
    return sorted(array, key=func)

def max(array:list, func=lambda x: x):
    if len(array) == 0:
        return None
    else:
        return __max(list, key=func)

def array(array:list):
    return random.sample(array, len(array))

def value_in_common(array1:list, array2:list):
    for v in array1:
        if v in array2:
            return True
    return False
