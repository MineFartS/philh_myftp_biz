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
    type: Literal['temp', 'keyring'] = 'disk'
    ) -> 'pkl | Ring':
    from .file import temp, pkl
    from .db import Ring

    if type == 'temp':
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
        args: list,
        wait: bool = False,
        terminal: Literal['cmd', 'ps', 'psfile', 'py', 'pym', 'vbs'] | None = 'cmd',
        dir: 'str | Path' = '.',
        nested: bool = True,
        hide: bool = False,
        cores: int = 4,
        timeout: int | None = None,
        autostart: bool = True
    ):
        from .array import new, stringify
        from .pc import Path, cwd
        from sys import executable

        # =====================================

        self.__wait = wait
        self.__nested = nested
        self.__hide = hide
        self.__file = Path(args[0])
        self.__cores = new([0, 1, 2, 3]).random(cores)
        self.__timeout = timeout

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
            self.__args = ['Powershell', '-Command']

        elif terminal == 'psfile':
            self.__args = ['Powershell', '-File']

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

        if autostart:
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

                self.__output += line

                if not self.__hide:
                    terminal.write(line, 'out')

    def __stderr(self):
        from .pc import terminal

        for line in self.__process.stderr:

            self.__output += line

            terminal.write(line, 'err')

    def start(self):
        from subprocess import Popen, PIPE
        from .time import Stopwatch
        from .pc import Task
       
        self.__process = Popen(
            args = self.__args,
            cwd = self.__dir.path,
            stdout = PIPE,
            stderr = PIPE,
            text = True,
            bufsize = 1
        )

        self.__task = Task(self.__process.pid)
        self.__stopwatch = Stopwatch().start()

        self.__output = ''

        self.wait = self.__process.wait

        thread(self.__stdout)
        thread(self.__stderr)
        thread(self.__background)

        if self.__wait:
            self.__process.wait()

    def finished(self) -> bool:
        return (not self.__task.exists())

    def restart(self) -> None:
        self.stop()
        self.start()

    def timed_out(self) -> bool | None:
        if self.__timeout:
            return (self.__stopwatch.elapsed() >= self.__timeout)

    def stop(self) -> None:
        self.__task.stop()
        self.__stopwatch.stop()

    def output(self,
        format: Literal['json', 'hex'] = None
    ):
        from . import json
        from .text import hex

        print(f"Output:'{self.__output.strip()}")

        if format == 'json':
            return json.loads(self.__output.strip())
        
        elif format == 'hex':
            return hex.decode(self.__output.strip())
        
        else:
            return self.__output.strip()

class errors:

    def FileNotFound(path:str):
        from errno import ENOENT
        from os import strerror

        return FileNotFoundError(ENOENT, strerror(ENOENT), path)
