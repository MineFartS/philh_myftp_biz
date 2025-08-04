from . import pc, other, array, text, file

import socket as _socket, tqdm, bs4, selenium, requests, lxml.etree, struct, urllib.request, browser_cookie3
import selenium.common, subprocess as sp, paramiko, qbittorrentapi, time

from selenium.webdriver import Firefox, FirefoxOptions, FirefoxService
from selenium.webdriver.common.by import By
from typing import Literal, Self, List, Generator

local_ip = '192.168.0.2'

def socket(timeout:int=10):
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    s.settimeout(timeout)
    return s

def mac2ip(mac):

    arp_table = other.run(['arp', '-a'], True, hide=True).output()

    for x in range(1, 256):

        ip = '192.168.0.' + str(x)

        if ip in arp_table:

            mac_ = array.filter(
                arp_table.split(ip)[1].split('\n')[0].split(' '),
                lambda x: '-' in x
            )[0]

            if mac_ == mac.replace(':', '-'):
                return ip

class conn:

    def __init__(self, conn:_socket.socket):
        self.conn = conn

    def send(self, data):

        data = text.hex.encode(data).encode()

        # Pack the length into a 4-byte header (e.g., using '!' for network byte order, 'I' for unsigned int)
        header = struct.pack('!I', len(data))

        # Send the header
        self.conn.sendall(header)

        # Send the actual data
        self.conn.sendall(data)

    def recv(self):

        # Unpack the length from the header
        length = struct.unpack('!I', 
            self.conn.recv(4)
        )[0]

        # Receive the actual data based on the unpacked length
        data = self.conn.recv(length).decode('utf-8')

        return text.hex.decode(data)

class host:

    def __init__(self, ip=local_ip, port:int=80):
        self.bindings = (ip, port)
        self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        self.start()
    
    def close(self):
        self.s.close()
        self.started = False

    def start(self):
        try:
            self.s.bind(self.bindings)
            self.s.listen()

            self.started = True
        except:
            self.started = False
            return

    def listen(self) -> Generator[conn]:
        while True:
            yield conn(self.s.accept()[0])

def client(ip=local_ip, port=80):
    try:
        conn_ = socket()
        conn_.connect((ip, port))
        return conn(conn_)
    except:
        return None

def port_listening(ip=local_ip, port:int=80):
    try:
        with socket() as s:
            s.settimeout(1)
            s.connect((ip, port))
            return True
    except (_socket.timeout, ConnectionRefusedError, OSError):
        return False
    
class Port:

    def __init__(self, host, port):
        
        self.port = port

        s = socket()

        try:
            s.connect((host, port))
            s.shutdown(_socket.SHUT_RDWR)
            self.free = False
        except _socket.error:
            self.free = True
        finally:
            s.close()

def find_open_port(min:int, max:int):
    for x in range(min, max+1):
        port = Port(local_ip, x)
        if port.free:
            return port.port

class ssh:

    def __init__(self, ip:str, username:str, password:str, timeout:int=None, port:int=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(ip, port, username, password, timeout=timeout)

    def run(self, command):

        # Execute a command
        stdout, stderr = self.client.exec_command(command)[1:]

        error_mess = stderr.read().decode()

        #
        class output:

            if len(error_mess) == 0:
                output = stdout.read().decode()
                error = False
            else:
                output = error_mess
                error = True
            
        return output

    def close(self):
        self.client.close()

class torrent:

    class qbit:

        def __init__(self):
            self.client = qbittorrentapi.Client(
                host = self.host(),
                port = 8080,
                username = 'admin',
                password = '3mW8{:t69Ho.',
                VERIFY_WEBUI_CERTIFICATE = False
            )

        def host(self):
            return mac2ip('00-15-5d-00-02-0b')

        def online(self):
            try:
                self.client.host = self.host()
                self.client.auth_log_in()
                return True
            
            except:
                return False

        def api(self):
            while not self.online():
                time.sleep(.1)
            return self.client

    tpb_url = "https://thepiratebay0.org/search/{}/1/99/0"

    def quality_from_title(title:str):

        title = title.lower()

        if '2160p' in title:
            return 2160
        
        if '1440p' in title:
            return 1440
        
        if '1080p' in title:
            return 1080
        
        if '720p' in title:
            if 'hdtv' in title:
                return 'hdtv'
            else:
                return 720
        
        if '480p' in title:
            return 480
        
        if '360p' in title:
            return 360
        
        if 'tvrip x264' in title:
            return 'tv'

    class queue:

        def find(tag):
            for t in torrent.qbit().api().torrents_info():
                if tag in t.tags:
                    return t

        class torrent:
            def __init__(self, t):
                
                self.hash = t.hash
                self.name = t.name

                seeders = t.num_complete
                remaining = t.size - t.downloaded
                self.priority = array.priority(seeders, remaining, True)

        def clear(rm_files:bool=True):
            qbit = torrent.qbit().api
            for t in qbit().torrents_info():
                qbit().torrents_delete(
                    torrent_hashes = t.hash,
                    delete_files = rm_files
                )

        def sort():

            api = torrent.qbit().api

            torrents = []

            for t in api().torrents_info():
                torrents.append(
                    torrent.queue.torrent(t)
                )

            torrents = array.sort(
                torrents,
                lambda t: t.priority
            )

            for x, t in enumerate(torrents):
                api().torrents_bottom_priority(t.hash)

    class Magnet:

        def state(self):
        
            class state:
                errored = None
                finished = None
                exists = None

            if self.get():
                enum = self.get().state_enum
                state.finished = enum.is_uploading or enum.is_complete
                state.errored = enum.is_errored
                state.exists = True
            else:
                state.exists = False
        
            return state

        def __init__(self, title=None, seeders=None, leechers=None, url=None, quality=None, size=None):
            
            self.title = title
            self.seeders = seeders
            self.leechers = leechers
            self.url = url
            self.quality = quality
            self.size = size

            self.qbit = torrent.qbit().api

        def start(self):
            self.qbit().torrents_add(
                self.url,
                save_path = 'G:/Scripts/__temp__/',
                tags = self.url
            )

        def get(self) -> Literal[qbittorrentapi.TorrentDictionary]:
            for t in self.qbit().torrents_info():
                if self.url in t.tags:
                    return t

        def restart(self):
            self.stop()
            self.start()
                
        def stop(self, rm_files:bool=True):
            torrent = self.get()
            if torrent:
                self.qbit().torrents_delete(
                    torrent_hashes = torrent.hash,
                    delete_files = rm_files
                )

        def files(self):
            torrent = self.get()
            for file in torrent.files:
                yield [
                    f'{torrent.save_path}/{file.name}',
                    file.size
                ]

    def searchTPB(*queries) -> Generator[Magnet]:
        for query in queries:

            query = text.rm(query, '.', "'")
            url = torrent.tpb_url.format(query)
            soup = static(url).soup

            for row in soup.select('tr:has(a.detLink)'):
                try:

                    title = row.select_one('a.detLink').text
                    details = row.select_one('font.detDesc').text

                    yield torrent.Magnet(
                        title = title,
                        seeders = int(row.select('td')[-2].text),
                        leechers = int(row.select('td')[-1].text),
                        url = row.select_one('a[href^="magnet:"]')['href'],
                        quality = torrent.quality_from_title(title),
                        size = pc.size.to_bytes(details.split('Size ')[1].split(',')[0])
                    )

                except:
                    pass

def get(**args):

    if 'headers' not in args:            
        args['headers'] = {}

    args['headers']['User-Agent'] = 'Mozilla/5.0'
    args['headers']['Accept-Language'] = 'en-US,en;q=0.5'

    while True:
        try:
            return requests.get(**args)
        except requests.exceptions.ConnectionError as e:
            pc.warn(e)

class api:

    def omdb(url='', params=[]):
        params['apikey'] = 'dc888719'
        return requests.get(
            url = 'https://www.omdbapi.com/' + url,
            params = params
        ).json()
    
    def numista(url='', params=[]):
        return requests.get(
            url = 'https://api.numista.com/v3/' + url,
            params = params,
            headers = {'Numista-API-Key': 'KzxGDZXGQ9aOQQHwnZSSDoj3S8dGcmJO9SLXxYk1'},
        ).json()
    
    def mojang(url='', params=[]):
        return requests.get(
            url = 'https://api.mojang.com/' + url,
            params = params
        ).json()
    
    def geysermc(url='', params=[]):
        return requests.get(
            url = 'https://api.geysermc.org/v2/' + url,
            params = params
        ).json()

    def __init__(self, url:str=None, params={}, headers=None):
        self.data = get(
            url = url,
            params = params,
            headers = headers,
        ).json()
    
    def __main__(self):
        return self.data

class soup:

    def convItems(self, soups):
        elements = []
        for s in soups:
            elements.append(soup(s))
        return elements

    by = Literal[
        'class', 'classname', 'class_name',
        'id',
        'xpath',
        'name',
        'attr', 'attribute'
    ]

    def __init__(self, soup:bs4.BeautifulSoup):
        self.soup = soup
        self.dom:lxml.etree._Element = lxml.etree.HTML(str(soup))

    def element(self, by:by, name:str) -> List[Self]:
        
        by = by.lower()

        if by in ['class', 'classname', 'class_name']:
            return self.convItems(
                self.soup.select(f'.{name}')
            )

        if by in ['id']:
            return self.convItems(
                self.soup.find_all(id=name)
            )

        if by in ['xpath']:
            return self.convItems(
                self.dom.xpath(name)
            )

        if by in ['name']:
            return self.convItems(
                self.soup.find_all(name=name)
            )

        if by in ['attr', 'attribute']:
            t, c = name.split('=')
            return self.convItems(
                self.soup.find_all(attrs={t: c})
            )

class browser:

    by = Literal['class', 'id', 'xpath', 'name', 'attr']
            
    def __init__(self, headless:bool=True, wait:int=20):
        
        self.via_with = False
        self.wait = wait

        service = FirefoxService()
        service.creation_flags = sp.CREATE_NO_WINDOW

        options = FirefoxOptions()
        options.add_argument("--disable-search-engine-choice-screen")
        if headless:
            options.add_argument("--headless")
        
        # Start Chrome Session with options
        self.session = Firefox(options, service)

        # Set Implicit Wait for session
        self.session.implicitly_wait(self.wait)

    def __enter__(self):
        self.via_with = True
        return self

    def __exit__(self, *_):
        if self.via_with:
            self.close()
    
    def run(self, code):
        return self.session.execute_script(code)

    def element(self, by:by, name, wait:bool=True):

        # Force 'by' input to lowercase
        by = by.lower()

        # Check if by is 'class'
        if by in ['class', 'classname', 'class_name']:
            
            if isinstance(name, list):
                name = (''.join([('.'+n) for n in name]))[1:]

            _by = By.CLASS_NAME

        # Check if by is 'id'
        if by in ['id']:
            _by = By.ID

        # Check if by is 'xpath'
        if by in ['xpath']:
            _by = By.XPATH

        # Check if by is 'name'
        if by in ['name']:
            _by = By.NAME

        # Check if by is 'attr'
        if by in ['attr', 'attribute']:
            _by = By.CSS_SELECTOR
            t, c = name.split('=')
            name = f"a[{t}='{c}']"

        elements = self.session.find_elements(_by, name)

        while (len(elements) == 0) and wait:
            elements = self.session.find_elements(_by, name)

        return elements

    def reload(self):
        self.session.refresh()

    def open(self, url):

        self.session.get(url)

        other.waitfor(
            self.run("return document.readyState") in ["complete", 'interactive']
        )

    def close(self):
        try:
            self.session.close()
        except selenium.common.exceptions.InvalidSessionIdException:
            pass

    class Profile:

        dir = "C:/Users/Administrator/AppData/Roaming/Mozilla/Firefox"

        def __init__(self, name):

            profiles = file.properties(self.dir + "/profiles.ini").read()

            for prof in profiles:
                if prof.startswith('Profile'):
                    if name == profiles[prof]['Name']:
                        self.dir = self.dir + '/' + profiles[prof]['Path']
                        return
                    
        def cookies(self):
            return browser_cookie3.firefox(self.dir + '/cookies.sqlite')

def static(url):
    return soup(
        bs4.BeautifulSoup(
            get(url=url).content,
            'html.parser'
        )
    )

def dynamic(url, driver=None):
    
    if driver is None:
        driver = browser()

    driver.open(url)

    return soup(bs4.BeautifulSoup(
        driver.session.page_source,
        'html.parser'
    ))

def download(url, path, show_progress:bool=True, cookies=None):

    r = get(
        url = url,
        stream = True,
        cookies = cookies
    )

    size = int(r.headers.get("content-length", 0))

    if show_progress:
        with tqdm.tqdm(total=size, unit="B", unit_scale=True) as progress_bar:
            with open(path, "wb") as file:
                for data in r.iter_content(1024):
                    progress_bar.update(len(data))
                    file.write(data)

    else:
        urllib.request.urlretrieve(url, path)
