from . import pc, web, text, array, time

import pickle, os, threading, sys, subprocess as sp
from typing import Literal

def waitfor(func):
    while not func():
        pc.wait(.1)

class var:

    def __init__(self, title, default='', temp=False):
        if temp:
            self.pkl = f'G:/Scripts/__temp__/var_{text.hex.encode(title)}.pkl'
        else:
            self.pkl = f'G:/Scripts/__cache__/var_{text.hex.encode(title)}.pkl'
        self.title = title
        self.default = default

    def read(self):
        try:
            return pickle.load(open(self.pkl, 'rb'))
        except:
            return self.default
        
    def save(self, value):
        return pickle.dump(value, open(self.pkl, 'wb'))

def thread(func, args=()):
    p = threading.Thread(target=func, args=args)
    p.start()
    return p

class run:

    def __args__(self, args, terminal):
            
        args = array.stringify(args)

        # =====================================

        if terminal == 'ext':

            exts = {
                'ps1' : 'ps',
                'py'  : 'py',
                'exe' : 'cmd',
                'bat' : 'cmd',
                'vbs' : 'vbs'
            }

            ext = pc.ext(args[0])
            if ext:
                terminal = exts[ ext.lower() ]

        # =====================================

        if terminal == 'cmd':
            return ['cmd', '/c'] + args

        elif terminal == 'ps':
            if pc.exists(args[0]):
                return ['Powershell', '-File'] + args
            else:
                return ['Powershell', '-Command'] + args

        elif terminal == 'py':
            return pc.exe.py + args

        elif terminal == 'pip':
            return pc.exe.pip + args

        elif terminal == 'pym':
            return pc.exe.mod + args
        
        elif terminal == 'vbs':
            return ['wscript'] + args

        else:
            return args
        
    terminals = Literal['cmd', 'ps', 'py', 'pip', 'pym', 'vbs']

    def __init__(self,
        args:list,
        wait:bool = False,
        terminal:terminals = 'cmd',
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
        for _ in time.every(.5):
            if self.finished():
                self.stop()
                return
            else:
                self.task.cores(*self.cores)

    def __stdout__(self):
        for line in self.process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

    def __stderr__(self):
        for line in self.process.stderr:
            sys.stdout.write(line)
            sys.stdout.flush()

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

    def finished(self):
        try:

            if self.params['timeout']:
                timed_out = self.stopwatch.elapsed() >= self.params['timeout']
            else:
                timed_out = False

            parent_dead = self.process.poll() != None

            return timed_out or parent_dead
        
        except:
            return True

    def stop(self):
        self.stopwatch.stop()
        self.task.stop()

    def output(self):
        return self.process.communicate()[0]
