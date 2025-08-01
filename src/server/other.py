from . import pc, web, text, array, time

import pickle, os, threading, sys, psutil, subprocess as sp
from typing import Literal

def waitfor(func):
    while not func():
        pc.wait(.1)

def alert(message):
    web.get(
            
        url = 'https://script.google.com/macros/s/AKfycbzPVIbhncFsVbjEY2erHn9Hm6MswrVBninlBh8iD9d0EzT4kJVCEWnkj1jU30TQGE2y/exec',

        params = {

            'email' : '6175437210@vtext.com',
            
            'subject' : time.now().stamp("%Y-%m-%d %H:%M:%S"),
            
            'message' : message

        }
            
    )

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

    def __args__(self, args:array.stringify, terminal):
            
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

    def __set_cores__(self):
        while True:
            
            if self.finished():
                self.stopwatch.stop()
                return
            
            else:
                for child in self.children():
                    try:
                        child.cpu_affinity(self.cores)
                    except:
                        pass

    def __output__(self):
        for line in self.process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

    def children(self):
        if psutil.pid_exists(self.parent.pid):
            return self.parent.children(True) + [self.parent]
        else:
            return []

    def start(self):
       
        self.process = sp.Popen(
            shell = self.params['nested'],
            args = self.params['args'],
            cwd = self.params['dir'],
            stdout = -1,
            stderr = -2,
            text = True
        )

        self.parent = psutil.Process(self.process.pid)

        self.stopwatch = time.Stopwatch().start()

        if not self.params['hide']:
            thread(self.__output__)

        thread(self.__set_cores__)

        if self.params['wait']:
            self.wait()

    def restart(self):
        self.stop()
        self.start()

    def finished(self):
        for _ in self.children():
            return False
        return True

    def stop(self):
        for pid in self.children():
            pid.terminate()

    def output(self):
        return self.process.stdout.read()

class log:
    def __init__(self, log_path=None):

        if log_path is None:
            self.f = None
        else:
            self.f = open(log_path, 'w')

    def __send__(self, message):
        message = text.rm_emojis(message, '#')
        print(message)
        if self.f != None:
            self.f.write(message)

    def file(self, detail, file):
        self.__send__(f"""
-----------------------------------------
{time.now().stamp('%Y/%m/%d %H:%M:%S')}
{detail}:
{file}
-----------------------------------------
    """) 

    def title(self, detail):
        self.__send__(f"\n |-------------- {detail} --------------|\n")

    def plain(self, text):
        self.__send__(text)
