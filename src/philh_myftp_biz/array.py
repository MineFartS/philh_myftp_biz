from . import pc, file

import json
import random as _random
from typing import Callable, Self

_max = max
_list = list
_filter = filter

lambda_ = lambda x: x

def stringify(array:list):
    for x, item in enumerate(array):
        array[x] = str(item)
    return array

class new[_T]:

    def __init__(self, list = []):

        if isinstance(list, (file.json, pc._var, file.pkl)):
            self.var = list

        elif isinstance(list, new):
            self.var = list.var

        else:
            self.var = file.pkl(
                file.temp('array', 'pkl')
            )
            self.var.save(generate(list))

        self.save = self.var.save
        self.read = self.var.read

    def append(self, item:_T):
        self.save(
            self.read() + [item]
        )

    def remove(self, item):
        
        arr = self.read()

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

    def sorted(self, func:Callable[[_T], Self]=lambda_) -> Self:
        data = sort(self.read(), func)
        return new(data)

    def sort(self, func:Callable[[_T], Self]=lambda_) -> None:
        self.save( self.sorted(func).read() )

    def max(self, func:Callable[[_T], Self]=lambda_) -> None | _T:
        if len(self) > 0:
            return max(self.read(), func)
    
    def filtered(self, func:Callable[[_T], Self]=lambda_) -> Self:
        data = filter(self.read(), func)
        return new(data)
    
    def filter(self, func:Callable[[_T], Self]=lambda_) -> None:
        self.save( filter(self.read(), func) )

    def random(self, n:int=1) -> Self:
        data = random.sample(self.read(), n)
        return new(data)

    def shuffle(self) -> None:
        self.save(shuffle(self.read()))
    
    def shuffled(self) -> Self:
        return new(shuffle(self.read()))

    def __str__(self):
        return json.dumps(self.read(), indent=2)

def generate(generator):
    return [x for x in generator]

def priority(_1:int, _2:int, reverse:bool=False):
    
    p = _1 + (_2 / (1000**1000))
    
    if reverse:
        p *= -1

    return p

class random:

    def sample(list, n:int=1):

        list = generate(list)

        if len(list) == 0:
            return None
        elif n > len(list):
            n = len(list)

        return _random.sample(list, n)

    def choice(list):

        list = generate(list)

        if len(list) > 0:
            return _random.choice(list)

def filter(list:generate, func=lambda_):
    return _list(_filter(func, list))

def sort(list:generate, func=lambda_):
    return sorted(list, key=func)

def max(list:generate, func=lambda_):
    if len(list) == 0:
        return None
    else:
        return _max(list, key=func)
    
def shuffle(list:generate):
    return _random.sample(list, len(list))

def value_in_common(list1:generate, list2:generate):
    for v in list1:
        if v in list2:
            return True
    return False
