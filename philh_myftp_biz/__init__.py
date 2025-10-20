from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .file import pkl
    from .db import Ring
    from .pc import Path

def args():
    from sys import argv
    from .array import auto_convert

    return auto_convert(argv[1:])

def var(
    title: str,
    default = '',
    type: Literal['cache', 'temp', 'keyring'] = 'cache'
    ) -> 'pkl | Ring':
    from .file import temp, cache, pkl
    from .db import Ring

    if type == 'cache':
        return pkl(
            path = cache('var', 'pkl', title),
            default = default
        )
    
    elif type == 'temp':
        return pkl(
            path = temp('var', 'pkl', title),
            default = default
        )

    elif type == 'keyring':
        ring = Ring('__variables__')
        return ring.Key(
            name = title,
            default = default
        )

def thread(func, args=()):
    from threading import Thread

    p = Thread(
        target = func,
        args = args
    )

    p.start()
    
    return p

class run:

    def __init__(self,
        args: list | str,
        wait: bool = False,
        terminal: Literal['cmd', 'ps', 'py', 'pym', 'vbs'] | None = 'cmd',
        dir: 'str | Path' = '.',
        nested: bool = True,
        hide: bool = False,
        cores: int = 4,
        timeout: int | None = None
    ):
        from .array import new, stringify
        from .pc import Path, cwd
        from sys import executable, maxsize

        # =====================================

        self.__wait = wait
        self.__nested = nested
        self.__hide = hide
        self.__file = Path(args[0])
        self.__cores = new([0, 1, 2, 3]).random(cores)
        
        if timeout:
            self.__timeout = timeout
        else:
            self.__timeout = maxsize

        if dir == '.':
            self.__dir = cwd()
        else:
            self.__dir = Path(dir)
        
        # =====================================   

        if terminal == 'ext':

            exts = {
                'ps1' : 'ps',
                'py'  : 'py',
                'exe' : 'cmd',
                'bat' : 'cmd',
                'vbs' : 'vbs'
            }

            ext = self.__file.ext()

            if ext:
                terminal = exts[ext]

        if terminal == 'cmd':
            self.__args = ['cmd', '/c']

        elif terminal == 'ps':
            if self.__file.exists():
                self.__args = ['Powershell', '-File']
            else:
                self.__args = ['Powershell', '-Command']

        elif terminal == 'py':
            self.__args = [executable]

        elif terminal == 'pym':
            self.__args = [executable, '-m']
        
        elif terminal == 'vbs':
            self.__args = ['wscript']

        else:
            self.__args = []

        if isinstance(args, (tuple, list)):
            self.__args += stringify(args)
        else:
            self.__args += [args]

        # =====================================

        self.start()

    def __background(self):
        from .time import every

        for _ in every(.1):
            if self.finished() or self.timed_out():
                self.stop()
                return
            else:
                self.__task.cores(*self.__cores)

    def __stdout(self):
        from .text import hex
        from .pc import cls, terminal

        cls_cmd = hex.encode('*** Clear Terminal ***')

        for line in self.__process.stdout:
            if cls_cmd in line:
                cls()
            elif len(line) > 0:
                terminal.write(line, 'out')

    def __stderr(self):
        from .pc import terminal

        for line in self.__process.stderr:
            terminal.write(line, 'err')

    def start(self):
        from subprocess import Popen
        from .time import Stopwatch, sleep
        from .pc import process
       
        self.__process = Popen(
            shell = self.__nested,
            args = self.__args,
            cwd = self.__dir.path,
            stdout = -1,
            stderr = -1,
            text = True
        )

        self.__task = process(self.__process.pid)
        self.__stopwatch = Stopwatch().start()

        self.wait = self.__process.wait

        if not self.__hide:
            thread(self.__stdout)
            thread(self.__stderr)

        thread(self.__background)

        if self.__wait:
            while not self.finished():
                time.sleep(.1)

    def finished(self) -> bool:
        return (not self.__task.alive())

    def restart(self) -> None:
        self.stop()
        self.start()

    def timed_out(self) -> bool:
        return self.__stopwatch.elapsed() > self.__timeout

    def stop(self) -> None:
        self.__stopwatch.stop()
        self.__task.stop()

    def output(self, process:bool=False):
        from .json import valid, loads
        from .text import hex
        
        output = self.__process.communicate()[0]
        
        if process:

            if hex.valid(output):
                return hex.decode(output)

            elif valid(output):
                return loads(output)

        return output

class errors:

    def FileNotFound(path:str):
        from errno import ENOENT
        from os import strerror

        return FileNotFoundError(ENOENT, strerror(ENOENT), path)
