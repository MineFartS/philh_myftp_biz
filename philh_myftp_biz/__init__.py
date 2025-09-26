from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
   from .file import pkl
   from .db import Ring

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
    from sys import maxsize

    def __init__(self,
        args: list | str,
        wait: bool = False,
        terminal: Literal['cmd', 'ps', 'py', 'pym', 'vbs', None] = 'cmd',
        dir = '.',
        nested: bool = True,
        hide: bool = False,
        cores: int = 4,
        timeout: int = maxsize
    ):
        from .array import new, stringify
        from .pc import Path
        from sys import executable
        from os import getcwd
  
        self.params = {
            'args' : [],
            'wait' : wait,
            'dir' : None,
            'nested' : nested,
            'hide' : hide,
            'cores' : cores,
            'timeout' : timeout
        }

        # =====================================

        if dir == '.':
            self.params['dir'] = getcwd()
        else:
            self.params['dir'] = dir

        # =====================================

        if isinstance(args, (tuple, list)):
            args = stringify(args)
        else:
            args = [args]

        file = Path(args[0])

        if terminal == 'ext':

            exts = {
                'ps1' : 'ps',
                'py'  : 'py',
                'exe' : 'cmd',
                'bat' : 'cmd',
                'vbs' : 'vbs'
            }

            if file.ext():
                terminal = exts[file.ext()]

        if terminal == 'cmd':
            self.params = ['cmd', '/c', *args]

        elif terminal == 'ps':
            if file.exists():
                self.params = ['Powershell', '-File', *args]
            else:
                self.params = ['Powershell', '-Command', *args]

        elif terminal == 'py':
            self.params = [executable, *args]

        elif terminal == 'pym':
            self.params = [executable, '-m', *args]
        
        elif terminal == 'vbs':
            self.params = ['wscript'] + args

        # =====================================

        self.cores = new([0, 1, 2, 3]).random(cores)

        self.start()

    def __background__(self):
        from .time import every

        for _ in every(.1):
            if self.finished() or self.timed_out():
                self.stop()
                return
            else:
                self.task.cores(*self.cores)

    def __stdout__(self):
        from .text import hex
        from .pc import cls, terminal

        cls_cmd = hex.encode('*** Clear Terminal ***')

        for line in self.process.stdout:
            if cls_cmd in line:
                cls()
            elif len(line) > 0:
                terminal.write(line, 'out')

    def __stderr__(self):
        from .pc import terminal

        for line in self.process.stderr:
            terminal.write(line, 'err')

    def start(self):
        from subprocess import Popen, PIPE
        from .time import Stopwatch
        from .pc import process
       
        self.process = Popen(
            shell = self.params['nested'],
            args = self.params['args'],
            cwd = self.params['dir'],
            stdout = PIPE,
            stderr = PIPE,
            text = True
        )

        self.task = process(self.process.pid)
        self.stopwatch = Stopwatch().start()

        self.wait = self.process.wait

        if not self.params['hide']:
            thread(self.__stdout__)
            thread(self.__stderr__)

        thread(self.__background__)

        if self.params['wait']:
            self.wait()

    def finished(self) -> bool:
        return (not self.task.alive())

    def restart(self) -> None:
        self.stop()
        self.start()

    def timed_out(self) -> bool:
        if self.params['timeout']:
            return self.stopwatch.elapsed() > self.params['timeout']
        else:
            return False

    def stop(self) -> None:
        self.stopwatch.stop()
        self.task.stop()

    def output(self, process:bool=False):
        from .json import valid, loads
        from .text import hex
        
        output = self.process.communicate()[0]
        
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
