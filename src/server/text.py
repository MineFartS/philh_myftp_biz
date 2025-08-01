import string, random as _random, dill, re

def int_stripper(string):
    for char in string:
        try:
            int(char)
        except ValueError:
            string = string.replace(char, '')
    return int(string)

def trimbychar(string, x, char):
    for _ in range(0, x):
        string = string[:string.rfind(char)]
    return string

class contains:
    def any(string, values):
        for v in values:
            if v in string:
                return True
        return False
    
    def all(string, values):
        for v in values:
            if v not in string:
                return False
        return True

def auto_convert(string):
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            try:
                return bool(string)
            except:
                return string

def rm(string:str, *values:str):
    for value in values:
        string = string.replace(value, '')
    return string

class hex:
    def decode(value):
        return dill.loads(bytes.fromhex(value))

    def encode(value):
        return dill.dumps(value).hex()

def random(length):
    return ''.join(_random.choices(string.ascii_uppercase + string.digits, k=length))

def includes_all(text, values):
    for value in values:
        if value not in text:
            return False
    return True

def includes_any(text, values):
    for value in values:
        if value in text:
            return True
    return False

def starts_with_any(text, values):
    return True in [text.startswith(v) for v in values]

def ends_with_any(text, values):
    return True in [text.endswith(v) for v in values]

def rm_emojis(text:string, sub:string=''):

    return re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+", flags=re.UNICODE).sub(
        sub.encode('unicode_escape').decode(),
        text.encode('utf-8').decode()
    )
