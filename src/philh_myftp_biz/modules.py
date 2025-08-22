from . import pc, other, text, file, time

from typing import Generator
_list = list

def output(data):
    pc.cls()
    print(';' + text.hex.encode(data) + ';')
    exit()

def input():
    args = []
    for a in other.args:
        args.append( text.hex.decode(a) )
    return args

class Module:

    def __init__(self, module:str):

        if isinstance(module, pc.Path):
            self.module = text.hex.encode(module.path)
            self.dir = module

        elif ('/' in module):
            self.module = text.hex.encode(module)
            self.dir = pc.Path(module)

        else:
            self.module = module
            self.dir = pc.Path(f'G:/Scripts/Modules/{module}')

        config = file.yaml(

            path = self.dir.child('config.yaml'),

            default = {
                'enabled' : False,
                'packages' : [],
                'watch_files' : []
            }
            
        ).read()

        self.lock = Lock(module)

        self.enabled = config['enabled']

        self.packages: _list[str] = config['packages']

        self.watch_files: _list[WatchFile] = []
        for path in config['watch_files']:
            self.watch_files += [WatchFile(
                module = self,
                path = pc.Path(self.dir + path)
            )]

    def run(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, _list(args), hide, True)

    def start(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, _list(args), hide, False)

    def file(self, *name:str):
        
        dir = self.dir.child( '/'.join(name[:-1]) )

        for p in dir.children():
            if (p.name().lower()) == (name[-1].lower()):
                return p

        raise other.errors.FileNotFound(self.dir.path + '.*')

class Process:

    def __init__(self, module:Module, args:str, hide, wait):
    
        self.module:Module = module

        file = self.module.file(*args[0].split('/'))

        args[0] = file.path

        if file.ext() == 'py':
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

        self.output = lambda: self.p.output(True)

class Lock:

    def __init__(self, module):
        self.module = module
        self.var = other.var(['Module Lock', module], False, True)

    def reset(self):
        self.var.save(False)

    def lock(self):
        self.var.save(True)

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

class WatchFile:
        
    def __init__(self, module:Module, path:pc.Path):

        self.path = path
        self.module = module

        self.var = path.var('__mtime__')
        
        self.var.save(
            value = self.path.mtime.get()
        )

    def modified(self):
        return self.var.read() != self.path.mtime.get()

def when_modified(*modules:Module):

    watch_files: _list[WatchFile] = []

    for module in modules:
        watch_files += module.watch_files

    while True:
        for wf in watch_files:
            if wf.modified():
                yield wf

        time.sleep(.25)

def list() -> Generator[Module]:
    
    path = pc.Path('G:/Scripts/Modules')
    
    for p in path.children():
    
        m = Module(p.name())
    
        if m.enabled:
            yield m
