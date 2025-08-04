from . import other, time, text, file, array

import os, shutil, pathlib, re, send2trash, sys, traceback, io, time as _time, ctypes, elevate, psutil
from inputimeout import inputimeout, TimeoutOccurred
from typing import Literal, Generator

_input = input
_print = print

isdir = os.path.isdir
isfile = os.path.isfile

stdout = sys.stdout

class temp:

    def dir():
        G = 'G:/Scripts/__temp__'
        C = pathlib.Path(os.environ['tmp']).as_posix() + '/server'

        if os.path.exists(G):
            return G
        else:
            mkdir(C)
            return C

    def file(name='', ext='ph'):
        return f'{temp.dir()}/{name}--{text.random(50)}.{ext}'

class cache:
    None

class terminal:
    
    def width():
        return shutil.get_terminal_size().columns
    
    def write(text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def del_last_line():
        cmd = "\033[A{}\033[A"
        spaces = (' ' * terminal.width())
        print(cmd.format(spaces), end='')

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def elevate():
        if not terminal.is_admin():
            elevate.elevate() # show_console=False

    def dash(p:int=100):
        _print(terminal.width() * (p//100) * '-')

def wait(s:int, print:bool=False):
    if print:
        _print('Waiting ...')
        for x in range(1, s+1):
            _print('{}/{} seconds'.format(x, s))
            _time.sleep(1)
    else:
        _time.sleep(s)
    
    return True

def cls():
    os.system('cls')

def exists(name, dir='.'):
    
    cwd = os.getcwd()
    os.chdir(dir)
    
    try:
        exists = os.path.exists(name)
    except:
        exists = False

    os.chdir(cwd)

    return exists

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

class print:

    colors = Literal[
        'BLACK',
        'RED',
        'GREEN',
        'YELLOW',
        'BLUE',
        'MAGENTA',
        'CYAN',
        'WHITE',
        'DEFAULT',
        None
    ]

    color_values = {
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

    def __init__(self, *args, pause:bool=False, color:colors='DEFAULT', sep=' ', end='\n', overwrite:bool=False):

        if color is None:
            return
        
        if overwrite:
            end = ''
            terminal.del_last_line()
        
        message = self.color_values[color.upper()]

        for arg in args:
            message += str(arg) + sep

        message = message[:-1] + self.color_values['DEFAULT'] + end

        if pause:
            input(message)
        else:
            _print(message, flush=True)

def is_seconds_old(path, seconds):
    if os.path.exists(path):
        return seconds_since_modified(path) >= seconds

def seconds_since_modified(path):

    now = time.now().unix
    mtime = os.path.getmtime(__as_posix__(path))

    return now - mtime

def children(path, recursive:bool=False):
    if recursive:
        for root, dirs, files in os.walk(path):
            for item in (dirs + files):
                yield os.path.join(root, item).replace('\\', '/')
    else:
        for p in pathlib.Path(path).iterdir():
            yield p.as_posix()

def __as_posix__(*input):

    if len(input) == 1:

        if isinstance(input[0], str):
            return pathlib.Path(input[0]).absolute().as_posix()
                        
        elif isinstance(input[0], pathlib.PurePath):
            return input[0].as_posix()
        
        else:
            return input[0].replace('\\', '/')
        
    else:
        return os.path.join(*input).replace('\\', '/')
    
def script_dir(__file__):
    return os.path.dirname( os.path.abspath(__file__) ).replace('\\', '/')

def sibling(path, item):
    return pathlib.Path(path).parent.joinpath(item).as_posix()

class mtime:

    def __init__(self, path:__as_posix__):
        self.path = path

    def set(self, mtime=None):
        if mtime is None:
            os.utime(self.path, (time.time(), time.time()))
        else:
            os.utime(self.path, (mtime, mtime))

    def get(self):
        return os.path.getmtime(self.path)

class var:
    
    def __init__(self, file, var, default=None):
        self.file = __as_posix__(file)
        self.default = default
        set_access(file).full()
        self.path = self.file + ':' + text.hex.encode(var)

    def read(self):
        try:
            value = open(self.path).read()
            return text.hex.decode(value)
        except:
            return self.default
        
    def save(self, value):
        m = mtime(self.file).get()
        
        open(self.path, 'w').write(
            text.hex.encode(value)
        )
        
        mtime(self.file).set(m)

class set_access:

    def __init__(self, path:__as_posix__, recursive:bool=False):
        
        self.paths = [path]
        
        if recursive and os.path.isdir(path):
            for p in children(path, True):
                self.paths.append(p)
    
    def readonly(self):
        for path in self.paths:
            os.chmod(path, 0o644)

    def full(self):
        for path in self.paths:
            os.chmod(path, 0o777)

def ext(path:__as_posix__):
    ext = os.path.splitext(path)[1][1:]
    if len(ext) > 0:
        return ext 

def type(path:__as_posix__):
    if os.path.isdir(path):
        return 'dir'
    else:
        try:
            return file.json("G:/Scripts/Resources/Mime Types/compiled.json").read() [ext(path)]
        except KeyError:
            return None

class cd:

    def __enter__(self):
        self.via_with = True

    def __exit__(self, *_):
        if self.via_with:
            self.back()

    def __init__(self, dir):

        self.via_with = False

        self.src = os.getcwd()

        self.dst = dir
        
        if os.path.isfile(self.dst):
            self.dst = parent(self.dst)
        
        self.open()

    def open(self):
        os.chdir(self.dst)

    def back(self):
        os.chdir(self.src)

def rename(src:__as_posix__, dst:__as_posix__, overwrite:bool=True):
    
    if type(dst) is None:
        dst += '.' + ext(src)

    with cd(src):
        try:
            os.rename(src, dst)
        except FileExistsError as e:
            if overwrite:
                rm(dst)
                os.rename(src, dst)
            else:
                warn(e)

def chext(path, ext):
    path = __as_posix__(path)
    return path[:path.rfind('.')+1] + ext

def name(path):
    path = __as_posix__(path).split('/')[-1]
    if '.' in path:
        return path[:path.rfind('.')]
    else:
        return path

def mkdir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except Exception as e:
        return e

class link:

    def resolve(path):
        return pathlib.Path(path).resolve().as_posix()

    def __init__(self, src, dest):

        if os.path.exists(src):
            set_access(src).full()
        if os.path.exists(dest):
            rm(dest)

        mkdir(src)
        mkdir(parent(dest))

        os.link(src, dest)

def parent(path):
    return pathlib.Path(path).parent.as_posix()

def relpath(file, root1, root2):
    return os.path.join(root2, os.path.relpath(file, root1)).replace('\\', '/')

def relscan(src, dst):

    items = []

    def scanner(src_, dst_):
        for item in os.listdir(src):

            s = os.path.join(src_, item)
            d = os.path.join(dst_, item)

            if os.path.isfile(s):
                items.append([s, d])

            elif os.path.isdir(s):
                scanner(s, d)
            
    scanner(src, dst)
    return items

def child(parent, child):
    return os.path.join(str(parent), str(child)).replace('\\', '/')

class rm:

    def trash(path):
        send2trash.send2trash(path)

    def erase(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def __init__(self, path:__as_posix__, trash:bool=True):
        if exists(path):

            set_access(path, True).full()

            if trash:
                try:
                    rm.trash(path)
                except:
                    rm.erase(path)
            else:
                rm.erase(path)

class exe:
    py = [sys.executable]
    mod = [sys.executable, '-m']
    pip = [sys.executable, '-m', 'pip']

def warn(exc: Exception):

    file = io.StringIO()
    traceback.print_exception(exc, file=file)

    _print(file.getvalue().rstrip())

class dots:
    
    def __init__(self, n:int):

        self.n = n
        self.dots = '.'

    def next(self):

        if len(self.dots) >= self.n:
            self.dots = ''

        self.dots += '.'

        return self.dots

def copy(src, dst, overwrite:bool=True, follow_links:bool=False):
    try:

        mkdir(parent(dst))
        
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)

    except KeyboardInterrupt as e:
        rm(dst)
        raise e

def move(src, dest, overwrite:bool=True, follow_links:bool=False):
    copy(src, dest, overwrite, follow_links)
    rm(src)

def input(prompt, timeout:int=None, default=None):

    if timeout:
        try:
            return inputimeout(prompt=prompt, timeout=timeout)
        except TimeoutOccurred:
            return default
    else:
        return _input(prompt)

def inuse(path):
    
    if os.path.exists(path):
        try:
            os.rename(path, path)
            return False
        except PermissionError:
            return True
    else:
        return False

class process:

    def __init__(self, id):

        self._processes = array.new()

        if isinstance(id, int):
            if exists(id):
                self._processes += psutil.Process(id)

        elif isinstance(id, str):
            for proc in psutil.process_iter():
                if self.exists(proc):
                    if proc.name().lower() == id.lower():
                        self._processes += proc

    def exists(self, proc):
        try:

            if isinstance(proc, int):
                proc = psutil.Process(proc)

            proc.name()

            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def processes(self) -> Generator[psutil.Process]:
        for proc in self._processes:
            if self.exists(proc):
                for child in proc.children(True):
                    if self.exists(child):
                        yield child

                yield proc

    def cores(self, *cores):
        for process in self.processes():
            process.cpu_affinity(cores)

    def stop(self):
        for process in self.processes():
            process.terminate()

class size:

    def to_bytes(string):

        match = re.search(
            r"(\d+(\.\d+)?)\s*([a-zA-Z]+)",
            string.strip()
        )

        value = float(match.group(1))

        unit = match.group(3).upper()
        unit = unit[0] + unit[-1]

        conv_factors = {
            'B' : 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }

        return value * conv_factors[unit]
