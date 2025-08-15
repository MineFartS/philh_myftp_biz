from . import num

import string, dill, re, shlex, io
import random as _random

IO = io.StringIO

def split(value:str, sep:str=None):
    if sep:
        return value.split(str(sep))
    else:
        return shlex.split(value)

def int_stripper(string:str):
    for char in string:
        try:
            int(char)
        except ValueError:
            string = string.replace(char, '')
    return int(string)

def trimbychar(string:str, x:int, char:str):
    for _ in range(0, x):
        string = string[:string.rfind(char)]
    return string

class contains:

    def any (
        string: str,
        values: list[str]
    ):
        for v in values:
            if v in string:
                return True
        return False
    
    def all (
        string: str,
        values: list[str]
    ):
        for v in values:
            if v not in string:
                return False
        return True

def auto_convert(string:str):

    if num.valid.int(string):
        return int(string)
    
    elif num.valid.float(string):
        return float(string)
    
    else:
        try:
            return bool(string)
        except:
            return string

def rm(string:str, *values:str):
    for value in values:
        string = string.replace(value, '')
    return string

class hex:

    def valid(value:str):
        try:
            hex.decode(value)
            return True
        except (EOFError, ValueError):
            return False

    def decode(value:str):
        if ';' in value:
            value = value.split(';')[1]
        return dill.loads(bytes.fromhex(value))

    def encode(value:str) -> str:
        return dill.dumps(value).hex()

def random(length):
    return ''.join(_random.choices(
        population = string.ascii_uppercase + string.digits,
        k = length
    ))

def starts_with_any (
    text: str,
    values: list[str]
):
    return True in [text.startswith(v) for v in values]

def ends_with_any (
    text: str,
    values: list[str]
):
    return True in [text.endswith(v) for v in values]

def rm_emojis(
    text: str,
    sub: str = ''
):
    regex = re.compile(
        "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags = re.UNICODE
    )

    return regex.sub(
        repl = sub.encode('unicode_escape').decode(),
        string = text.encode('utf-8').decode()
    )
