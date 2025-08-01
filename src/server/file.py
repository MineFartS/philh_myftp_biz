from . import pc, other, text as _text

import json as _json, os, tqdm, bs4, yaml as _yaml, configobj, zipfile, csv, dill, subprocess as sp
from xml.etree import ElementTree as ET

class xml:

    def __init__(self, file, title):
        self.root = ET.Element(title)
        self.file = file

    def child(element, title, text):
        e = ET.SubElement(element, title)
        e.text = text
        return e

    def save(self):
        tree = ET.ElementTree(self.root)
        tree.write(self.file, encoding="utf-8", xml_declaration=True)
        d = bs4.BeautifulSoup(open(self.file), 'xml').prettify()
        open(self.file, 'w').write(d)

class pkl:

    def __init__(self, path, default=None):

        self.path = pc.__as_posix__(path)
        pc.mkdir(pc.parent(path))

        self.default = default

    def read(self):
        try:
            with open(self.path, 'rb') as f:
                return dill.load(f)
        except:
            return self.default

    def save(self, value):
        with open(self.path, 'wb') as f:
            dill.dump(value, f)

class vdisk:

    via_with = False

    def __enter__(self):
        self.via_with = True
        if not self.mount():
            return

    def __exit__(self, *_):
        if self.via_with:
            self.dismount()

    def list(self=None):
        try:
            r = vdisk.__ps__(30, 'Get-Volume | Select-Object DriveLetter, FileSystem, Size, SizeRemaining, HealthStatus | ConvertTo-Json')
            data = _json.loads(r.stdout)
            return data # TODO
        except:
            return []

    def __ps__(self, cmd):
    
        if isinstance(self, int):
            timeout = self
        else:
            timeout = self.timeout

        try:
            return sp.run(['Powershell', '-Command', cmd], timeout=timeout, stdout=sp.DEVNULL)
        except sp.TimeoutExpired:
            return None

    def reset(self=None):

        other.run(['mountvol', '/r'], True)

        for VHD in vdisk.list():
            vdisk.__ps__(30, f'Dismount-DiskImage -ImagePath "{VHD}"')

    def __init__(self, VHD, MNT, timeout=30, ReadOnly:bool=False):
        self.VHD = VHD
        self.MNT = MNT
        self.timeout = timeout
        self.ReadOnly = {True:' -ReadOnly', False:''} [ReadOnly]

    def mount(self):
        self.dismount()
        pc.mkdir(self.MNT)
        return self.__ps__(
            f'Mount-VHD -Path "{self.VHD}" -NoDriveLetter -Passthru {self.ReadOnly} | Get-Disk | Get-Partition | Add-PartitionAccessPath -AccessPath "{self.MNT}"'
        )

    def dismount(self):
        tm = self.__ps__(f'Dismount-DiskImage -ImagePath "{self.VHD}"')

        if self.MNT != None:
            pc.rm(self.MNT)

        return tm

class json:

    def class_2_json(class_object):
        class empty:
            ''
        default_names = dir(empty)

        json_obj = {}

        for name in dir(class_object):
            if name not in default_names:
                json_obj[name] = getattr(class_object, name)

        return json_obj                

    def __init__(self, path, default={}, encode:bool=False):
        self.path = path
        pc.mkdir(pc.parent(path))
        self.encode = encode
        self.default = default
    
    def read(self):
        try:
            data = _json.load(open(self.path))
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
            fp = open(self.path, 'w'),
            indent = 3
        )

class properties:

    def __init__(self, path, default=''):
        self.path = path

        pc.mkdir(pc.parent(path))

        if not os.path.exists(path):
            open(path, 'w').write(default)

        pc.set_access(self.path).full()
    
    def read(self):
        return configobj.ConfigObj(self.path).dict()
    
    def save(self, data):

        config = configobj.ConfigObj(self.path)

        for name in data:
            config[name] = data[name]

        config.write()

class yaml:
    
    def __init__(self, path, default=''):
        self.path = path
        self.default = default

        pc.mkdir(pc.parent(path))

        pc.set_access(self.path).full()
    
    def read(self):
        try:
            return _yaml.safe_load(
                open(self.path).read()
            )
        except:
            return self.default
    
    def save(self, data):
        with open(self.path, 'w') as file:
            _yaml.dump(data, file, default_flow_style=False, sort_keys=False)

class text:

    def __init__(self, path, default='', encoding='utf-8'):
        self.path = path
        self.encoding = encoding

        pc.mkdir(pc.parent(path))

        if not os.path.exists(path):
            open(path, 'w', encoding=encoding).write(default)

        pc.set_access(self.path).full()
    
    def read(self):
        return open(self.path, 'r', encoding=self.encoding).read()
    
    def save(self, data):
        open(
            self.path, 'w',
            encoding = self.encoding
        ).write(data)

    def append(self, data, newline:bool=True):
        open(
            self.path, 'a',
            encoding = self.encoding,
            newline = {True:'\n', False:''} [newline]
        ).write(data)

class archive:

    def __init__(self, file):
        self.file = file
        self.zip = zipfile.ZipFile(file, 'r')
        self.files = self.zip.namelist()

    def extractFile(self, file, path):
        try:
            self.zip.extract(file, path)
        except zipfile.BadZipFile:
            pass

    def extractAll(self, path, show_progress:bool=True):
        
        pc.mkdir(path)

        if show_progress:
            with tqdm.tqdm(total=len(self.files), unit=' file') as pbar:
                for file in self.files:
                    pbar.update(1)
                    self.extractFile(file, path)
        else:
            self.zip.extractall(path)

class csv:

    def __init__(self, path, default=''):
        self.path = path

    def read(self):
        with open(self.path) as csvfile:
            return csv.reader(csvfile)
        
    def write(self, data):
        with open(self.path) as csvfile:
            return csv.writer(csvfile).writerows(data)
