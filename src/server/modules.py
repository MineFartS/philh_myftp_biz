from . import pc, other, text, file

import os, sys, json
_list = list

def when_modified(*modules):

    watch_files = []
    for module in modules:
        for var in module.watch_files:
            watch_files.append([
                var.file,
                var,
                pc.mtime(var.file)
            ])

    while True:

        for path, var, mtime in watch_files:
            if var.read() != mtime.get():
                
                yield path
                
                for path, var, mtime in watch_files:
                    var.save(mtime.get())
        
        pc.wait(.25)

def list():
    for p in pc.children('G:/Scripts/Modules'):
        yield Module(pc.name(p))

def output(data):
    pc.cls()
    print(';' + text.hex.encode(data) + ';')
    exit()

def input():
    args = []
    for a in sys.argv[1:]:
        args.append( text.hex.decode(a) )
    return args

class Module:

    def __init__(self, module):

        self.module = module
        self.dir = f'G:/Scripts/Modules/{module}'
        self.configfile = self.dir + '/config.yaml'

        if pc.exists(self.configfile):

            config = file.yaml(self.configfile).read()

            self.lock = Lock(module)
            self.enabled = config['enabled']

            self.watch_files = []
            for path in config['watch_files']:
                var = pc.var(self.dir + path, '__mtime__')
                var.save( os.path.getmtime(var.file) )
                self.watch_files += [var]        

    def run(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, _list(args), hide, True)
    
    def start(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, _list(args), hide, False)

    def file(self, *name:str):
        file = name[-1].lower()
        dir = (self.dir + '/') + ('/'.join(name[:-1]))

        for p in pc.children(dir):
            if pc.name(p).lower() == file:
                return p

class Process:

    def __init__(self, module:Module, args:str, hide, wait):
    
        self.module:Module = module

        args[0] = self.module.file(*args[0].split('/'))

        self.encoded = pc.ext(args[0]) == 'py'
        if self.encoded:
            for x in range(1, len(args)):
                args[x] = text.hex.encode(args[x])

        self.p = other.run(
            args = args,
            wait = wait,
            hide = hide,
            terminal = 'ext',
            cores = 3
        )

        self.start = self.p.start
        self.stop = self.p.stop
        self.restart = self.p.restart
        self.finished = self.p.finished

    def output(self):

        o = self.p.output()

        try:
            return text.hex.decode(
                o.split(';')[1]
            )
        except:
            try:
                return json.loads(text.rm(o, '\n').strip())
            except:
                return o

class Lock:

    def __init__(self, module):
        self.module = module
        self.var = other.var(['Module Lock', module], False, True)

    def reset(self):
        self.var.save(False)

    def startup(self, timeout:int=15):
        if self.var.read():

            pc.cls()
            
            pc.print(
                f'The "{self.module}" module is locked',
                color = 'RED'
            )
            
            pc.print(
                f'This prompt will timeout in {str(timeout)} seconds',
                color = 'YELLOW'
            )

            input = pc.input(
                "Press the 'Enter' key to override",
                timeout = timeout
            )
            
            if input is None:
                exit()
            else:
                pc.cls()

        else:
            self.var.save(True)
    
    def finish(self):
        self.var.save(False)