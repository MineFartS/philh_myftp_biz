from typing import Generator

def output(data):
    from .text import hex
    from .pc import cls

    cls()
    print(';' + hex.encode(data) + ';')
    exit()

def input():
    from . import args as __args
    from .text import hex

    args = []
    for a in __args:
        args.append( hex.decode(a) )
    return args

def when_modified(*modules:'Module'):
    from .time import sleep

    watch_files: list['WatchFile'] = []

    for module in modules:
        watch_files += module.watch_files

    while True:
        for wf in watch_files:
            if wf.modified():
                yield wf

        sleep(.25)

def fetch() -> Generator['Module']:
    from .pc import Path
    
    path = Path('G:/Scripts/Modules')
    
    for p in path.children():
    
        m = Module(p.name())
    
        if m.enabled:
            yield m

class Module:

    def __init__(self, module:str):
        from .pc import Path
        from .text import hex
        from .file import yaml

        if isinstance(module, Path):
            self.name = hex.encode(module.path)
            self.dir = module

        elif ('/' in module):
            self.name = hex.encode(module)
            self.dir = Path(module)

        else:
            self.name = module
            self.dir = Path(f'G:/Scripts/Modules/{module}')

        config = yaml(

            path = self.dir.child('config.yaml'),

            default = {
                'enabled' : False,
                'packages' : [],
                'watch_files' : []
            }
            
        ).read()

        self.lock = Lock(self)

        self.enabled = config['enabled']

        self.packages: list[str] = config['packages']

        self.watch_files: list[WatchFile] = []
        for path in config['watch_files']:
            self.watch_files += [WatchFile(
                module = self,
                path = self.dir.child(path)
            )]

    def run(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, list(args), hide, True)

    def start(self, *args, hide:bool=False):
        if self.enabled:
            return Process(self, list(args), hide, False)

    def file(self, *name:str):
        from . import errors

        parts: list[str] = []
        for n in name:
            parts += n.split('/')
        
        dir = self.dir.child(*parts[:-1])

        for p in dir.children():
            if (p.name().lower()) == (parts[-1].lower()):
                return p

        raise errors.FileNotFound(dir.path + '.*')

class Process:

    def __init__(self, module:Module, args:str, hide, wait):
        from .text import hex
        from . import run
    
        self.module = module

        file = module.file(args[0])

        args[0] = file.path

        if file.ext() == 'py':
            for x in range(1, len(args)):
                args[x] = hex.encode(args[x])

        self.p = run(
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

    def __init__(self, module:Module):
        from . import var

        self.module = module
        
        self.var = var(
            title = f'Module Lock {module.name}',
            default = False,
            temp = True
        )

    def reset(self):
        self.var.save(False)

    def lock(self):
        self.var.save(True)

    def startup(self, timeout:int=15):
        from .pc import print, cls, input

        if self.var.read():

            cls()
            
            print(
                f'The "{self.module.name}" module is locked',
                color = 'RED'
            )
            
            print(
                f'This prompt will timeout in {str(timeout)} seconds',
                color = 'YELLOW'
            )

            input = input(
                "Press the 'Enter' key to override",
                timeout = timeout
            )
            
            if input is None:
                exit()
            else:
                cls()

        else:
            self.var.save(True)
    
    def finish(self):
        self.var.save(False)

class WatchFile:
    
    from .pc import Path
    def __init__(self, module:Module, path:Path):

        self.path = path
        self.module = module

        self.var = path.var('__mtime__')
        
        self.var.save(
            value = self.path.mtime.get()
        )

    def modified(self):
        return self.var.read() != self.path.mtime.get()
