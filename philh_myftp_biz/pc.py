from typing import Literal, Self, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .db import colors
    from psutil import Process

__input = input
__print = print

def NAME():
    from socket import gethostname
    hn = gethostname()
    del gethostname
    return hn

def SERVER_LAN():
    from .web import ping
    p = ping('192.168.1.2')
    del ping
    return p

def OS() -> Literal['windows', 'unix']:
    from os import name

    return {
        True: 'windows',
        False: 'unix'
    } [name == 'nt']

class Path:

    def __init__(self, *input):
        from pathlib import Path as libPath, PurePath
        from os import path

        # ==================================

        if len(input) > 1:
            joined: str = path.join(*input)
            self.path = joined.replace('\\', '/')

        elif isinstance(input[0], Path):
            self.path = input[0].path

        elif isinstance(input[0], str):
            self.path = libPath(input[0]).absolute().as_posix()

        elif isinstance(input[0], PurePath):
            self.path = input[0].as_posix()

        elif isinstance(input[0], libPath):
            self.path = input[0].as_posix()

        # ==================================

        # Declare path string
        self.path: str = self.path.replace('\\', '/')

        # Declare 'pathlib.Path' attribute
        self.__Path = libPath(self.path)

        # Link 'exists', 'isfile', & 'isdir' functions from 'self.__Path'
        self.exists = self.__Path.exists
        self.isfile = self.__Path.is_file
        self.isdir = self.__Path.is_dir

        # Declare 'set_access'
        self.set_access = _set_access(self)

        # Declare 'mtime'
        self.mtime = _mtime(self)

        # ==================================

        # Add trailing '/'
        if (not self.path.endswith('/')) and self.isdir():
            self.path += '/'

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
        return Path(self.__Path.absolute())
    
    def resolute(self):
        return Path(self.__Path.resolve(True))
    
    def child(self,
        *name: str
    ):

        if self.isfile():
            raise TypeError("Parent path cannot be a file")
        
        elif len(name) > 1:
            return Path(self.path + '/'.join(name))
        
        elif name[0].startswith('/'):
            return Path(self.path + name[0][1:])
            
        else:
            return Path(self.path + name[0])

    def __str__(self):
        return self.path

    def __eq__(self, other):

        if isinstance(other, Path):
            return (self.path == other.path)
        else:
            return False

    def islink(self):
        return self.__Path.is_symlink() or self.__Path.is_junction()

    def size(self) -> int:
        from os import path

        if self.isfile():
            return path.getsize(self.path)

    def children(self) -> Generator[Self]:
        for p in self.__Path.iterdir():
            yield Path(p)

    def descendants(self) -> Generator[Self]:
        for root, dirs, files in self.__Path.walk():
            for item in (dirs + files):
                yield Path(root, item)

    def parent(self):
        return Path(self.__Path.parent)

    def var(self, name, default=None):
        return _var(self, name, default)
    
    def sibling(self, item):
        return self.parent().child(item)
    
    def ext(self):
        from os import path

        ext = path.splitext(self.path)[1][1:]
        if len(ext) > 0:
            return ext.lower()

    def type(self):
        from .db import mime_types

        types = mime_types

        if self.isdir():
            return 'dir'

        elif self.ext() in types:
            return types[self.ext()]

    def delete(self):
        from send2trash import send2trash
        from shutil import rmtree
        from os import remove

        if self.exists():
            
            self.set_access.full()

            try:
                send2trash(self.path)

            except OSError:

                if self.isdir():
                    rmtree(self.path)
                else:
                    remove(self.path)

    def rename(self, dst, overwrite:bool=True):
        from os import rename

        src = self
        dst = Path(dst)

        if dst.ext() is None:
            dst.chext(self.ext())
        
        with src.cd():
            try:
                rename(src.path, dst.path)
            except FileExistsError as e:
                if overwrite:
                    dst.delete()
                    rename(src, dst)
                else:
                    raise e

    def name(self):

        name = self.__Path.name

        # Check if file has ext
        if self.ext():
            # Return name without ext
            return name[:name.rfind('.')]

        else:
            # Return filename
            return name

    def seg(self, i:int=-1):
        return self.path.split('/') [i]

    def copy(
        self,
        dst: (Self | str)
    ):
        from shutil import copyfile, copytree
        
        dst = Path(dst)

        try:
            
            mkdir(dst.parent())

            if self.isfile():

                if dst.isdir():
                    dst = dst.child( self.seg() )

                if dst.exists():
                    dst.delete()

                copyfile(
                    src = self.path, 
                    dst = dst.path
                )

            else:
                copytree(
                    src = self.path,
                    dst = dst.path,
                    dirs_exist_ok = True
                )

        except Exception as e:
            print('Undoing ...')
            dst.delete()
            raise e

    def move(self, dst):
        self.copy(dst)
        self.delete()

    def inuse(self):
        from os import rename

        if self.exists():
            try:
                rename(self.path, self.path)
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
    from os import getcwd

    return Path(getcwd())

def pause():
    from os import system

    if OS() == 'windows':
        system('pause')
    else:
        pass # TODO

class cd:

    def __enter__(self):
        self.via_with = True

    def __exit__(self, *_):
        if self.via_with:
            self.back()

    def __init__(self, dir):
        from os import getcwd

        self.via_with = False

        self.src = getcwd()

        self.dst = Path(dir)
        
        if self.dst.isfile():
            self.dst = self.dst.parent()

        self.open()

    def open(self):
        from os import chdir

        chdir(self.dst.path)

    def back(self):
        from os import chdir
        
        chdir(self.src.path)

class terminal:
    
    def width():
        from shutil import get_terminal_size
        return get_terminal_size().columns

    def write(
        text,
        stream: Literal['out', 'err'] = 'out',
        flush: bool = True
    ):
        from io import StringIO
        import sys
        
        stream: StringIO = getattr(sys, 'std'+stream)
        
        stream.write(text)
    
        if flush:
            stream.flush()

    def del_last_line():
        cmd = "\033[A{}\033[A"
        spaces = (' ' * terminal.width())
        print(cmd.format(spaces), end='')

    def is_elevated():
        try:
            from ctypes import windll
            return windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def elevate():
        if not terminal.is_elevated():
            from elevate import elevate
            elevate() # show_console=False

    def dash(p:int=100):
        __print(terminal.width() * (p//100) * '-')

def cls():
    from .text import hex
    from os import system

    __print(hex.encode('*** Clear Terminal ***'))
    system('cls')

class power:

    def restart(t:int=30):
        from . import run

        run(
            args = ['shutdown', '/r', '/t', t],
            wait = True
        )

    def shutdown(t:int=30):    
        from . import run
        
        run(
            args = ['shutdown', '/s', '/t', t],
            wait = True
        )

    def abort():
        from . import run
        
        run(
            args = ['shutdown', '/a'],
            wait = True
        )

def print(
    *args,
    pause: bool = False,
    color: 'colors.names' = 'DEFAULT',
    sep: str = ' ',
    end: str = '\n',
    overwrite: bool = False
):
    from .db import colors
    
    if overwrite:
        end = ''
        terminal.del_last_line()
    
    message = colors.values[color.upper()]
    for arg in args:
        message += str(arg) + sep

    message = message[:-1] + colors.values['DEFAULT'] + end

    if pause:
        input(message)
    else:
        terminal.write(message)

def script_dir(__file__):
    from os import path

    return Path(path.abspath(__file__)).parent()

class _mtime:

    def __init__(self, path:Path):
        self.path = path

    def set(self, mtime=None):
        from .time import now
        from os import utime

        if mtime:
            utime(self.path.path, (mtime, mtime))
        else:
            now = now().unix
            utime(self.path.path, (now, now))

    def get(self):
        from os import path

        return path.getmtime(self.path.path)
    
    def stopwatch(self):
        from .time import Stopwatch
        SW = Stopwatch()
        SW.start_time = self.get()
        return SW

class _var:

    def __init__(self,
        file: Path,
        title: str,
        default = None
    ):
        from .text import hex

        self.file = file
        self.title = title
        self.default = default

        self.path = file.path + ':' + hex.encode(title)

        file.set_access.full()

    def read(self):
        from .text import hex

        try:
            value = open(self.path).read()
            return hex.decode(value)
        except OSError:
            return self.default
        
    def save(self, value):
        from .text import hex
        
        try:
            m = _mtime(self.file).get()

            open(self.path, 'w').write(
                hex.encode(value)
            )

            _mtime(self.file).set(m)
        except OSError:
            print(
                f"Error setting var '{self.title}' at '{str(self.file)}'",
                color = 'RED'
            )

class _set_access:

    def __init__(self, path:'Path'):
        self.path = path

    def __paths(self) -> Generator['Path']:

        yield self.path

        if self.path.isdir():
            for path in self.path.descendants():
                yield path
    
    def readonly(self):
        from os import chmod

        for path in self.__paths():
            chmod(str(path), 0o644)

    def full(self):
        from os import chmod

        for path in self.__paths():
            chmod(str(path), 0o777)

def mkdir(path:str|Path):
    from os import makedirs

    makedirs(str(path), exist_ok=True)

def link(src, dst):
    from os import link

    src = Path(src)
    dst = Path(dst)

    if dst.exists():
        dst.delete()

    mkdir(dst.parent())

    link(
        src = src.path,
        dst = dst.path
    )

def relpath(file, root1, root2):
    from os import path
    
    return Path(

        str(root2),
        
        path.relpath(
            str(file),
            str(root1)
        )
    
    )

def relscan(src:Path, dst:Path) -> list[list[Path]]:

    items = []

    def scanner(src_:Path, dst_:Path):
        from os import listdir

        for item in listdir(src.path):

            s = src_.child(item)
            d = dst_.child(item)

            if s.isfile():
                items.append([s, d])

            elif s.isdir():
                scanner(s, d)
            
    scanner(src, dst)
    return items

def warn(exc: Exception):
    from io import StringIO
    from traceback import print_exception
    
    IO = StringIO()

    print_exception(exc, file=IO)
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

        from inputimeout import inputimeout, TimeoutOccurred

        try:
            return inputimeout(prompt=prompt, timeout=timeout)
    
        except TimeoutOccurred:
            return default
        
        finally:
            del inputimeout, TimeoutOccurred
    
    else:
        return __input(prompt)

class Task:

    def __init__(self, id):
        self.id = id

    def __scanner(self) -> Generator['Process']:
        from psutil import process_iter, Process, NoSuchProcess

        main = None

        if isinstance(self.id, int):
            try:
                main = Process(self.id)
            except NoSuchProcess:
                pass

        elif isinstance(self.id, str):
            for proc in process_iter():
                if proc.name().lower() == self.id.lower():
                    main = Process(proc.pid)
                    break

        if main:
            if main.is_running():
                for child in main.children(True):
                    yield Process(child.pid)

    def cores(self, *cores):
        from psutil import NoSuchProcess, AccessDenied

        for p in self.__scanner():
            try:
                p.cpu_affinity(cores)
            except (NoSuchProcess, AccessDenied):
                pass

    def stop(self):
        for p in self.__scanner():
            p.terminate()

    def exists(self):
        processes = list(self.__scanner())
        return len(processes) > 0
