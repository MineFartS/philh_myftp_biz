from . import other, time, text, array, json, num, db

import os, shutil, pathlib, re, send2trash, sys, traceback, io, ctypes, elevate, psutil
from inputimeout import inputimeout, TimeoutOccurred
from typing import Literal, Self, Generator

_input = input
_print = print

OS: Literal['windows', 'unix'] = {
    True: 'windows',
    False: 'unix'
} [os.name == 'nt']

class Path:

    def __init__(self, *input):

        # ==================================

        if len(input) == 1:

            if isinstance(input[0], Path):
                self.path = input[0].path

            elif isinstance(input[0], str):
                self.path = pathlib.Path(input[0]).absolute().as_posix()

            elif isinstance(input[0], pathlib.PurePath):
                self.path = input[0].as_posix()
            
            else:
                _print(input)
                exit()
                self.path = input[0]
        
        else:
            self.path = os.path.join(*input).replace('\\', '/')

        # ==================================

        self.Path = pathlib.Path(self.path)

        self.exists = self.Path.exists
        self.isfile = self.Path.is_file
        self.isdir = self.Path.is_dir

        self.set_access = _set_access(self)

        self.mtime = _mtime(self)

        # ==================================

    def chext(self, ext):

        dst = self.path

        if self.ext():
            dst = dst[:dst.rfind('.')+1] + ext
        else:
            dst += '.' + ext

        if self.exists():
            self.rename(dst)
        
        self.path = dst

    def cd(self):
        if self.isfile():
            return cd(self.parent().path)
        else:
            return cd(self.path)

    def absolute(self):
        return Path(self.Path.absolute())
    
    def resolute(self):
        return Path(self.Path.resolve(True))
    
    def child(self, name):
        return Path(self.Path.joinpath(name))

    def __str__(self):
        return self.path

    def islink(self):
        return self.Path.is_symlink() or self.Path.is_junction()

    def size(self) -> int:
        if self.isfile():
            return os.path.getsize(self.path)

    def children(self) -> Generator[Self]:
        for p in self.Path.iterdir():
            yield Path(p)

    def descendants(self) -> Generator[Self]:
        for root, dirs, files in self.Path.walk():
            for item in (dirs + files):
                yield Path(root, item)

    def parent(self):
        return Path(self.Path.parent)

    def var(self, name, default=None):
        return __var(self, name, default)
    
    def sibling(self, item):
        return self.parent().child(item)
    
    def ext(self):
        ext = os.path.splitext(self.path)[1][1:]
        if len(ext) > 0:
            return ext.lower()

    def type(self):

        types = db.mime_types

        if self.isdir():
            return 'dir'

        elif self.ext() in types:
            return types[self.ext()]

    def delete(self):
        if self.exists():
            
            self.set_access.full()

            try:
                send2trash.send2trash(self.path)

            except OSError:

                if self.isdir():
                    shutil.rmtree(self.path)
                else:
                    os.remove(self.path)

    def rename(self, dst, overwrite:bool=True):

        src = self
        dst = Path(dst)

        if dst.ext() is None:
            dst.chext(self.ext())
        
        with src.cd():
            try:
                os.rename(src.path, dst.path)
            except FileExistsError as e:
                if overwrite:
                    dst.delete()
                    os.rename(src, dst)
                else:
                    raise e

    def name(self):
        if self.ext():
            return self.path[:self.path.rfind('.')].split('/')[-1]
        else:
            return self.path.split('/')[-1]

    def copy(self, dst: Self | str):
        
        dst = Path(dst)

        try:
            
            mkdir(dst.parent())

            if self.isfile():
                
                if dst.isfile():
                    shutil.copyfile(
                        src = self.path, 
                        dst = dst.path
                    )
                else:
                    shutil.copyfile(
                        src = self.path, 
                        dst = dst.child(self.name() + '.').path
                    )

            else:
                shutil.copytree(self.path, dst.path, dirs_exist_ok=True)

        except Exception as e:
            print('Undoing ...')
            dst.delete()
            raise e

    def move(self, dst):
        self.copy(dst)
        self.delete()

    def inuse(self):
        if self.exists():
            try:
                os.rename(self.path, self.path)
                return False
            except PermissionError:
                return True
        else:
            return False

    def raw(self):
        if self.isfile():
            return self.open('rb').read()
        
    def read(self):
        return self.open().read()
    
    def write(self, value=''):
        self.open('w').write(value)

    def open(self, mode='r'):
        return open(self.path, mode)

def cwd():
    return Path(os.getcwd())

class cd:

    def __enter__(self):
        self.via_with = True

    def __exit__(self, *_):
        if self.via_with:
            self.back()

    def __init__(self, dir):

        self.via_with = False

        self.src = os.getcwd()

        self.dst = Path(dir)
        
        if self.dst.isfile():
            self.dst = self.dst.parent()

        self.open()

    def open(self):
        os.chdir(self.dst.path)

    def back(self):
        os.chdir(self.src.path)

class terminal:
    
    def width():
        return shutil.get_terminal_size().columns

    def write(text, stream:Literal['out', 'err']='out'):
        stream:io.StringIO = getattr(sys, 'std'+stream)
        stream.write(text)
        stream.flush()

    def del_last_line():
        cmd = "\033[A{}\033[A"
        spaces = (' ' * terminal.width())
        print(cmd.format(spaces), end='')

    def is_elevated():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def elevate():
        if not terminal.is_elevated():
            elevate.elevate() # show_console=False

    def dash(p:int=100):
        _print(terminal.width() * (p//100) * '-')

def cls():
    _print(text.hex.encode('*** Clear Terminal ***'))
    os.system('cls')

class power:

    def restart(t:int=30):
        other.run(
            args = ['shutdown', '/r', '/t', t],
            wait = True
        )

    def shutdown(t:int=30):    
        other.run(
            args = ['shutdown', '/s', '/t', t],
            wait = True
        )

    def abort():
        other.run(
            args = ['shutdown', '/a'],
            wait = True
        )

def print(
    *args,
    pause: bool = False,
    color: db.colors.names = 'DEFAULT',
    sep: str = ' ',
    end: str = '\n',
    overwrite: bool = False
):
    
    if overwrite:
        end = ''
        terminal.del_last_line()
    
    message = db.colors.values[color.upper()]
    for arg in args:
        message += str(arg) + sep

    message = message[:-1] + db.colors.values['DEFAULT'] + end

    if pause:
        input(message)
    else:
        terminal.write(message)

def script_dir(__file__):
    return Path(os.path.abspath(__file__)).parent()

class _mtime:

    def __init__(self, path:Path):
        self.path = path

    def set(self, mtime=None):
        if mtime:
            os.utime(self.path.path, (mtime, mtime))
        else:
            now = time.now().unix
            os.utime(self.path.path, (now, now))

    def get(self):
        return os.path.getmtime(self.path.path)
    
    def stopwatch(self):
        SW = time.Stopwatch()
        SW.start_time = self.get()
        return SW

class __var:

    def __init__(self, file:Path, var, default=None):
        
        self.file = file
        self.default = default
        

        self.path = file.path + ':' + text.hex.encode(var)

        file.set_access.full()

    def read(self):
        try:
            value = open(self.path).read()
            return text.hex.decode(value)
        except:
            return self.default
        
    def save(self, value):
        m = _mtime(self.file).get()
        
        open(self.path, 'w').write(
            text.hex.encode(value)
        )
        
        _mtime(self.file).set(m)

class _set_access:

    def __init__(self, path:Path):
        self.path = path

    def __paths(self):

        yield self.path

        if self.path.isdir():
            for path in self.path.descendants():
                yield path
    
    def readonly(self):
        for path in self.__paths():
            path.Path.chmod(0o644)

    def full(self):
        for path in self.__paths():
            path.Path.chmod(0o777)

def mkdir(path:str|Path):
    os.makedirs(str(path), exist_ok=True)

def link(src, dst):

    src = Path(src)
    dst = Path(dst)

    if dst.exists():
        dst.delete()

    mkdir(dst.parent())

    os.link(
        src = src.path,
        dst = dst.path
    )

def relpath(file, root1, root2):
    return Path(

        str(root2),
        
        os.path.relpath(
            str(file),
            str(root1)
        )
    
    )

def relscan(src:Path, dst:Path) -> list[list[Path]]:

    items = []

    def scanner(src_:Path, dst_:Path):
        for item in os.listdir(src):

            s = src_.child(item)
            d = dst_.child(item)

            if s.isfile():
                items.append([s, d])

            elif s.isdir():
                scanner(s, d)
            
    scanner(src, dst)
    return items

def warn(exc: Exception):
    IO = io.StringIO()
    traceback.print_exception(exc, file=IO)
    terminal.write(IO.getvalue(), 'err')

class dots:
    
    def __init__(self, n:int):

        self.n = n
        self.dots = '.'

    def next(self):

        if len(self.dots) >= self.n:
            self.dots = ''

        self.dots += '.'

        return self.dots

def input(prompt, timeout:int=None, default=None):

    if timeout:
        try:
            return inputimeout(prompt=prompt, timeout=timeout)
        except TimeoutOccurred:
            return default
    else:
        return _input(prompt)

class process:

    exceptions = psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError

    def exists(pid:int):
        try:
            psutil.Process(pid)
            return True
        except process.exceptions:
            return False

    class Process:

        def __init__(self, pid:int):
            try:
                self.process = psutil.Process(pid)
            except process.exceptions:
                self.process = None

        def stop(self):
            if self.exists():
                self.process.terminate()

        def exists(self):
            try:
                self.process.as_dict()
                return True
            except process.exceptions:
                return False

        def children(self) -> Generator[Self]:
            if self.exists():
                for child in self.process.children(True):
                    if process.exists(child.pid):
                        yield process.Process(child.pid)

        def cores(self, *cores):
            if self.exists():
                self.process.cpu_affinity(cores)

    def __init__(self, id):
        self.id = id

    def scanner(self):
        if isinstance(self.id, int):
            yield process.Process(self.id)

        elif isinstance(self.id, str):
            for proc in psutil.process_iter():
                if proc.name().lower() == self.id.lower():
                    yield process.Process(proc.pid)

    def cores(self, *cores):
        for process in self.scanner():
            for child in process.children():
                child.cores(*cores)
            process.cores(*cores)

    def stop(self):
        for process in self.scanner():
            for child in process.children():
                child.stop()
            process.stop()

    def alive(self):
        items = array.generate(self.scanner())
        return len(items) > 0

def is_duplicate(file1, file2):
    data1 = open(file1, 'rb').read()
    data2 = open(file2, 'rb').read()
    return data1 == data2

class duplicates:

    class Group:

        def __init__(self):
            self.files: list[Path] = array.new()
            self.duplicates: list[Path] = array.new()

        def __iadd__(self, path:Path):
            
            if path not in self.files:
                self.files += [path]

            raw_files = array.new()

            for file in self.files:
                
                raw = file.raw()

                if raw in raw_files:
                    self.files -= file
                    self.duplicates += file
                else:
                    raw_files += raw

            return self

    def __init__(self):
        self.dirs: list[Path] = array.new()
        self.groups: dict[int, duplicates.Group] = json.new()

    def __iadd__(self, dir):
        self.dirs += [Path(dir)]
        return self
    
    def scan(self):

        groups: dict[int, duplicates.Group] = {}

        for dir in self.dirs:
            for file in dir.children():

                if file.size not in self.groups:
                    groups[file.size] = [self.Group()]

                groups[file.size] += [file]

        return groups

    def clean(self):
        groups = self.scan()
        for size, group in groups.items():
            for file in group.duplicates:
                file.delete()

    def file_exists(self, path):
        
        file = Path(path)
        
        groups = self.scan()
        for size, group in groups.items():
            
            if file.size() == int(size):
                group += file
                return file in group.duplicates

class size:

    def to_bytes(string:str):

        match = re.search(
            r"(\d+(\.\d+)?)\s*([a-zA-Z]+)",
            string.strip()
        )

        value = float(match.group(1))

        unit = match.group(3).upper()
        unit = unit[0] + unit[-1]

        return value * db.size.conv_factors[unit]

    def from_bytes(
        value: int | float,
        unit: db.size.units | None = None,
        ndigits: int = num.max
    ):

        format = lambda unit: round(
            number = (float(value) / db.size.conv_factors[unit]),
            ndigits = ndigits
        )

        if unit:
            return str(format(unit)) + ' ' + unit
        else:
            r = 0
            for unit in reversed(db.size.conv_factors):
                r = format(unit)
                if r >= 1:            
                    return str(r) + ' ' + unit
