from . import pc, other, text as _text, time

import tqdm, bs4, configobj, zipfile, dill, tomli_w, tempfile, os
from xml.etree import ElementTree as ET

import csv as _csv
import toml as _toml
import yaml as _yaml
import json as _json

class __quickfile:

    def __init__(self, folder:str):
        self.folder = folder

    def dir(self):

        G = pc.Path('G:/Scripts/' + self.folder)
        C = pc.Path(tempfile.gettempdir() + '/server/' + self.folder)

        if G.exists():
            return G
        else:
            pc.mkdir(C)
            return C 

    def new(
        self,
        name: str = 'undefined',
        ext: str = 'ph',
        id: str = None
    ):

        if id:
            id = str(id)
        else:
            id = _text.random(50)

        return self.dir().child(f'{name}-{id}.{ext}')

temp = __quickfile('temp').new
cache = __quickfile('cache').new

class xml:

    def __init__(self, path, title):
        self.root = ET.Element(title)
        self.path = pc.Path(path)

    def child(element, title, text):
        e = ET.SubElement(element, title)
        e.text = text
        return e

    def save(self):
        
        tree = ET.ElementTree(self.root)
        
        tree.write(self.path.path, encoding="utf-8", xml_declaration=True)
        
        d = bs4.BeautifulSoup(self.path.open(), 'xml').prettify()

        self.path.write(d)

class pkl:

    def __init__(self, path, default=None):
        self.path = pc.Path(path)
        self.default = default

    def read(self):
        try:
            with self.path.open('rb') as f:
                return dill.load(f)
        except:
            return self.default

    def save(self, value):
        with self.path.open('wb') as f:
            dill.dump(value, f)

class vdisk:

    class File:

        via_with = False

        def __enter__(self):
            self.via_with = True
            if not self.mount():
                return

        def __exit__(self, *_):
            if self.via_with:
                self.dismount()

        def __init__(self, VHD, MNT, timeout:int=30, ReadOnly:bool=False):
            self.VHD = pc.Path(VHD)
            self.MNT = pc.Path(MNT)
            self.timeout = timeout
            self.ReadOnly = {True:' -ReadOnly', False:''} [ReadOnly]

        def mount(self):

            self.dismount()

            return vdisk.run(
                cmd = f'Mount-VHD -Path "{self.VHD}" -NoDriveLetter -Passthru {self.ReadOnly} | Get-Disk | Get-Partition | Add-PartitionAccessPath -AccessPath "{self.MNT}"',
                timeout = self.timeout
            )

        def dismount(self):

            vdisk.run(
                cmd = f'Dismount-DiskImage -ImagePath "{self.VHD}"',
                timeout = self.timeout
            )

            self.MNT.delete()

    def list(self=None):
        try:
            p = vdisk.run(
                cmd = 'Get-Volume | Select-Object DriveLetter, FileSystem, Size, SizeRemaining, HealthStatus | ConvertTo-Json'
            )
            return _json.loads(p.output())
        except:
            return []

    def reset(self=None):

        other.run(['mountvol', '/r'], True)

        for VHD in vdisk.list():
            vdisk.run(
                cmd = f'Dismount-DiskImage -ImagePath "{VHD}"'
            )

    def run(cmd, timeout:int=30):
        return other.run(
            args = [cmd],
            wait = True,
            terminal = 'ps',
            hide = True,
            timeout = timeout
        )

class json:

    def __init__(self, path, default={}, encode:bool=False):
        self.path = pc.Path(path)
        self.encode = encode
        self.default = default
    
    def read(self):
        try:
            data = _json.load(self.path.open())
            if self.encode:
                return _text.hex.decode(data)
            else:
                return data
        except:
            return self.default

    def save(self, data):
        
        if self.encode:
            data = _text.hex.encode(data)

        _json.dump(
            obj = data,
            fp = self.path.open('w'),
            indent = 3
        )

class properties:

    def __init__(self, path, default=''):
        self.path = pc.Path(path)
        self.default = default
    
    def __obj(self):
        return configobj.ConfigObj(self.path.path)

    def read(self):
        try:
            return self.__obj().dict()
        except:
            return self.default
    
    def save(self, data):

        config = self.__obj()

        for name in data:
            config[name] = data[name]

        config.write()

class yaml:
    
    def __init__(self, path, default={}):
        self.path = pc.Path(path)
        self.default = default
    
    def read(self):
        try:

            with self.path.open() as f:
                data = _yaml.safe_load(f)

            if data is None:
                return self.default
            else:
                return data

        except:
            return self.default
    
    def save(self, data):
        with self.path.open('w') as file:
            _yaml.dump(data, file, default_flow_style=False, sort_keys=False)

class text:

    def __init__(self, path, default=''):
        self.path = pc.Path(path)
        self.default = default
    
    def read(self):
        try:
            self.path.read()
        except:
            return self.default
    
    def save(self, data):
        self.path.write(data)

class archive:

    def __init__(self, file):
        self.file = pc.Path(file)
        self.zip = zipfile.ZipFile(self.file.path)
        self.files = self.zip.namelist()

    def extractFile(self, file, path):
        try:
            self.zip.extract(file, path)
        except zipfile.BadZipFile as e:
            pc.warn(e)

    def extractAll(self, path, show_progress:bool=True):
        
        dst = pc.Path(path)

        pc.mkdir(dst)

        if show_progress:
            with tqdm.tqdm(total=len(self.files), unit=' file') as pbar:
                for file in self.files:
                    pbar.update(1)
                    self.extractFile(file, path)
        else:
            self.zip.extractall(path)

class csv:

    def __init__(self, path, default=''):
        self.path = pc.Path(path)
        self.default = default

    def read(self):
        try:
            with self.path.open() as csvfile:
                return _csv.reader(csvfile)
        except:
            return self.default

    def write(self, data):
        with self.path.open('w') as csvfile:
            _csv.writer(csvfile).writerows(data)

class toml:

    def __init__(self, path, default=''):
        self.path = pc.Path(path)
        self.default = default

    def read(self):
        try:
            with self.path.open() as f:
                return _toml.load(f)
        except:
            return self.default
        
    def save(self, data):
        with self.path.open('wb') as f:
            tomli_w.dump(data, f, indent=2)
