from . import pc, text, array, time, file, json

import os, threading, sys, errno
from typing import Literal
import subprocess as sp

args = [text.auto_convert(a) for a in sys.argv[1:]]

def waitfor(func):
    while not func():
        time.sleep(.1)

def var(title, default='', temp=False) -> file.pkl:

    args = 'var', 'pkl', text.hex.encode(title)

    if temp:
        path = file.temp(*args)
    else:
        path = file.cache(*args)

    return file.pkl(path, default)

def thread(func, args=()):
    p = threading.Thread(target=func, args=args)
    p.start()
    return p

class run:

    def __args__(self, args, terminal):
            
        args = array.stringify(args)

        file = pc.Path(args[0])

        # =====================================

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

        # =====================================

        if terminal == 'cmd':
            return ['cmd', '/c'] + args

        elif terminal == 'ps':
            if file.exists():
                return ['Powershell', '-File'] + args
            else:
                return ['Powershell', '-Command'] + args

        elif terminal == 'py':
            return [sys.executable, *args]

        elif terminal == 'pip':
            return [sys.executable, '-m', 'pip', *args]

        elif terminal == 'pym':
            return [sys.executable, '-m', *args]
        
        elif terminal == 'vbs':
            return ['wscript'] + args

        else:
            return args

    def __init__(self,
        args:list,
        wait:bool = False,
        terminal: Literal['cmd', 'ps', 'py', 'pip', 'pym', 'vbs'] = 'cmd',
        dir = os.getcwd(),
        nested:bool = True,
        hide:bool = False,
        cores:int = 4,
        timeout:int = None
    ):
        
        self.params = {
            'args' : self.__args__(args, terminal),
            'wait' : wait,
            'dir' : dir,
            'nested' : nested,
            'hide' : hide,
            'cores' : cores,
            'timeout' : timeout
        }

        self.cores = array.new([0, 1, 2, 3]).random(cores)

        self.start()

    def wait(self):
        self.process.wait()

    def __background__(self):
        for _ in time.every(.1):
            if self.finished() or self.timed_out():
                self.stop()
                return
            else:
                self.task.cores(*self.cores)

    def __stdout__(self):
        
        cls_cmd = text.hex.encode('*** Clear Terminal ***')

        for line in self.process.stdout:
            if cls_cmd in line:
                pc.cls()
            elif len(line) > 0:
                pc.terminal.write(line, 'out')

    def __stderr__(self):
        for line in self.process.stderr:
            pc.terminal.write(line, 'err')

    def start(self):
       
        self.process = sp.Popen(
            shell = self.params['nested'],
            args = self.params['args'],
            cwd = self.params['dir'],
            stdout = sp.PIPE,
            stderr = sp.PIPE,
            text = True
        )

        self.task = pc.process(self.process.pid)
        self.stopwatch = time.Stopwatch().start()

        if not self.params['hide']:
            thread(self.__stdout__)
            thread(self.__stderr__)

        thread(self.__background__)

        if self.params['wait']:
            self.wait()

    def restart(self):
        self.stop()
        self.start()

    def timed_out(self):
        if self.params['timeout']:
            return self.stopwatch.elapsed() > self.params['timeout']
        else:
            return False

    def finished(self):
        return self.task.alive()

    def stop(self):
        self.stopwatch.stop()
        self.task.stop()

    def output(self, process:bool=False):
        
        output = self.process.communicate()[0]
        
        if process:

            if text.hex.valid(output):
                return text.hex.decode(output)

            elif json.valid(output):
                return json.loads(output)

        return output

class errors:

    def FileNotFound(path:str):
        return FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
