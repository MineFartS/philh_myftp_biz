from typing import Literal, Self, Generator, TYPE_CHECKING
from quicksocketpy import host, client, socket

if TYPE_CHECKING:
    from .pc import Path
    from requests import Response
    from bs4 import BeautifulSoup

def IP(
    method: Literal['local', 'public'] = 'local'
):
    from socket import gethostname, gethostbyname

    if not online():
        return None

    elif method == 'local':
        return gethostbyname(gethostname())
    
    elif method == 'public':
        return get('https://api.ipify.org').text

online = lambda: ping('1.1.1.1')

def ping(
    addr: str,
    timeout: int = 3
):
    from ping3 import ping as __ping

    try:

        p = __ping(
            dest_addr = addr,
            timeout = timeout
        )

        return bool(p)
    
    except OSError:
        return False

def mac2ip(mac):
    from .array import filter
    from .__init__ import run
    from .pc import OS

    if OS() == 'windows':
        arp_table = run(['arp', '-a'], True, hide=True).output()

    base = '.'.join(IP().split('.')[:-1]) + '.{}'

    for x in range(1, 256):

        ip = base.format(x)

        if ip in arp_table:

            mac_ = filter(
                arp_table.split(ip)[1].split('\n')[0].split(' '),
                lambda x: '-' in x
            )[0]

            if mac_ == mac.replace(':', '-'):
                return ip

def port_listening(ip=IP(), port:int=80):
    from socket import timeout

    try:
        with socket() as s:
            s.settimeout(1)
            s.connect((ip, port))
            return True
    except (timeout, ConnectionRefusedError, OSError):
        return False
    
class Port:

    def __init__(self, host, port):

        from socket import error, SHUT_RDWR

        self.port = port

        s = socket()

        try:
            s.connect((host, port))
            s.shutdown(SHUT_RDWR)
            self.free = False
        except error:
            self.free = True
        finally:
            s.close()

def find_open_port(min:int, max:int):
    for x in range(min, max+1):
        port = Port(IP(), x)
        if port.free:
            return port.port

class ssh:

    def __init__(self, ip:str, username:str, password:str, timeout:int=None, port:int=22):

        from paramiko import SSHClient, AutoAddPolicy

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
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

class Magnet:

    __qualityTable: dict[str, Literal[360, 480, 720, 1080, 1440, 2160, 'tv', 'hdtv']] = {
        'hdtv': 'hdtv',
        'tvrip': 'tv',
        '2160p': 2160,
        '1440p': 1440,
        '1080p': 1080,
        '720p': 720,
        '480p': 480,
        '360p': 360
    }

    def __init__(self,
        title: str = None,
        seeders: int = None,
        leechers: int = None,
        url: str = None,
        size: str = None
    ):
            
        self.title = title.lower()
        self.seeders = seeders
        self.leechers = leechers
        self.url = url
        self.size = size

        self.quality = None
        for term in self.__qualityTable:
            if term in title.lower():
                self.quality = self.__qualityTable[term]

def get(
    url: str,
    params: dict = {},
    headers: dict = {},
    stream: bool = None,
    cookies = None
) -> 'Response':
    from requests import get as __get
    from requests.exceptions import ConnectionError
    from .pc import warn

    headers['User-Agent'] = 'Mozilla/5.0'
    headers['Accept-Language'] = 'en-US,en;q=0.5'

    while True:
        try:
            return __get(
                url = url,
                params = params,
                headers = headers,
                stream = stream,
                cookies = cookies
            )
        except ConnectionError as e:
            warn(e)

class api:

    """
    Wrappers for many types of APIs
    """
    
    def __init__(self,
        url: str = None,
        params = {},
        headers = None
    ):
        
        """
        Get Webpage as json
        """

        self.data = get(
            url = url,
            params = params,
            headers = headers,
        ).json()
    
    def __main__(self):
        return self.data

    def omdb(url='', params=[]):
        params['apikey'] = 'dc888719'
        return get(
            url = f'https://www.omdbapi.com/{url}',
            params = params
        ).json()
    
    def numista(url='', params=[]):
        return get(
            url = f'https://api.numista.com/v3/{url}',
            params = params,
            headers = {'Numista-API-Key': 'KzxGDZXGQ9aOQQHwnZSSDoj3S8dGcmJO9SLXxYk1'},
        ).json()
    
    def mojang(url='', params=[]):
        return get(
            url = f'https://api.mojang.com/{url}',
            params = params
        ).json()
    
    def geysermc(url='', params=[]):
        return get(
            url = f'https://api.geysermc.org/v2/{url}',
            params = params
        ).json()

    class qBitTorrent:

        def __init__(self,
            host: str,
            username: str,
            password: str,
            port: int = 8080
        ):
            from qbittorrentapi import Client

            self.__rclient = Client(
                host = host,
                port = port,
                username = username,
                password = password,
                VERIFY_WEBUI_CERTIFICATE = False
            )

        def __client(self):
            from qbittorrentapi import LoginFailed, Forbidden403Error

            while True:

                try:
                    self.__rclient.auth_log_in()
                    return self.__rclient
                
                except (LoginFailed, Forbidden403Error):
                    pass

        def start(self, magnet:Magnet):
            self.__client().torrents_add(
                magnet.url,
                save_path = 'E:/__temp__/',
                tags = magnet.url
            )

        def files(self, magnet:Magnet) -> Generator[list['Path', float]]:
            from .pc import Path
            
            for t in self.__client().torrents_info():
                if magnet.url in t.tags:
                    for file in t.files:
                        yield [
                            Path(f'{t.save_path}/{file.name}'),
                            file.size
                        ]

        def stop(self,
            magnet: Magnet,
            rm_files: bool = True
        ):
            for t in self.__client().torrents_info():
                if magnet.url in t.tags:
                    t.delete(rm_files)
                    return

        def clear(self, rm_files:bool=True):
            for t in self.__client().torrents_info():
                t.delete(rm_files)

        def sort(self):
            from .array import sort, priority
            from qbittorrentapi import TorrentDictionary

            items: list[TorrentDictionary] = sort(
                list(self.__client().torrents_info()),
                lambda t: priority(
                    _1 = t.num_complete, # Seeders
                    _2 = (t.size - t.downloaded), # Remaining
                    reverse = True
                )
            )

            for t in items:
                t.bottom_priority()

    class thePirateBay:

        url = "https://thepiratebay0.org/search/{}/1/99/0"

        def search(*queries) -> Generator[Magnet]:
            from .text import rm
            from .db import size

            for query in queries:

                query = rm(query, '.', "'")
                url = api.thePirateBay.url.format(query)
                soup = static(url).soup

                for row in soup.select('tr:has(a.detLink)'):
                    try:

                        title: str = row.select_one('a.detLink').text
                        details: str = row.select_one('font.detDesc').text

                        yield Magnet(
                            title = title,
                            seeders = int(row.select('td')[-2].text),
                            leechers = int(row.select('td')[-1].text),
                            url = row.select_one('a[href^="magnet:"]')['href'],
                            size = size.to_bytes(details.split('Size ')[1].split(',')[0])
                        )

                    except:
                        pass

class soup:

    def convItems(self, soups):
        elements = []
        for s in soups:
            elements.append(soup(s))
        return elements
    
    def __init__(self, soup:BeautifulSoup):
        """
        Wrapper for bs4.BeautifulSoup
        """
        
        from lxml.etree import _Element, HTML

        self.dom:_Element = HTML(str(soup))
        self.soup = soup

    def element(self,
        by: Literal['class', 'id', 'xpath', 'name', 'attr'],
        name: str
    ) -> list[Self]:
        """
        Get List of Elements by query
        """

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
    from selenium.webdriver.remote.webelement import WebElement
            
    def __init__(
        self,
        headless: bool = True,
        wait: int = 20,
        cookies: (list[dict] | None) = None,
        debug: bool = False
    ):
        """
        Wrapper for FireFox Selenium Session
        """
        from selenium.webdriver import FirefoxService, FirefoxOptions, Firefox
        from selenium.common.exceptions import InvalidCookieDomainException
        from subprocess import CREATE_NO_WINDOW
        
        self.via_with = False
        self.wait = wait
        self.__debug_enabled = debug

        service = FirefoxService()
        service.creation_flags = CREATE_NO_WINDOW

        options = FirefoxOptions()
        options.add_argument("--disable-search-engine-choice-screen")        
        if headless:
            options.add_argument("--headless")

        # Start Chrome Session with options
        self.__session = Firefox(options, service)

        if cookies:
            for cookie in cookies:
                try:
                    self.__session.add_cookie(cookie)
                except InvalidCookieDomainException:
                    pass

        # Set Implicit Wait for session
        self.__session.implicitly_wait(self.wait)

        self.current_url = self.__session.current_url

        self.reload = self.__session.refresh
        self.run = self.__session.execute_script

    def __enter__(self):
        self.via_with = True
        return self

    def __exit__(self, *_):
        if self.via_with:
            self.close()
    
    def __debug(self,
        title: str,
        data: dict ={}
        ):
        from .json import dumps
        
        if self.__debug_enabled:
            print(title+':', dumps(data))

    def element(self,
        by: Literal['class', 'id', 'xpath', 'name', 'attr'],
        name: str,
        wait: bool = True
    ) -> list[WebElement]:
        """
        Get List of Elements by query
        """
        from selenium.webdriver.common.by import By

        # Force 'by' input to lowercase
        by = by.lower()

        # Check if by is 'class'
        if by == 'class':
            
            if isinstance(name, list):
                name = '.'.join(name)

            _by = By.CLASS_NAME

        # Check if by is 'id'
        if by == 'id':
            _by = By.ID

        # Check if by is 'xpath'
        if by == 'xpath':
            _by = By.XPATH

        # Check if by is 'name'
        if by == 'name':
            _by = By.NAME

        # Check if by is 'attr'
        if by == 'attr':
            _by = By.CSS_SELECTOR
            t, c = name.split('=')
            name = f"a[{t}='{c}']"

        self.__debug(
            title = "Finding Element", 
            data = {'by': by, 'name':name}
        )

        if wait:

            while True:

                elements = self.__session.find_elements(_by, name)

                if len(elements) > 0:
                    return elements

        else:
            return self.__session.find_elements(_by, name)

    def open(self,
        url: str,
        wait: bool = True
    ):
        
        # Open the url
        self.__session.get(url)

        # Print Debug Messsage
        self.__debug(
            title = "Opening", 
            data = {'url':url}
        )

        # Check if 'wait' is True
        if wait:

            # Wait until page is loaded
            while self.run("return document.readyState") != "complete":
                pass

            return

    def close(self):
        from selenium.common.exceptions import InvalidSessionIdException
        
        # Print Debug Message
        self.__debug('Closing Session')

        try:
            # Exit Session
            self.__session.close()
        except InvalidSessionIdException:
            pass

    def soup(self) -> soup:
        from bs4 import BeautifulSoup
        
        # Return soup object with the current page's html
        return soup(BeautifulSoup(
            self.__session.page_source,
            'html.parser'
        ))

def static(url) -> soup:
    """
    Save a webpage as a static soup
    """

    from bs4 import BeautifulSoup

    return soup(
        BeautifulSoup(
            get(url=url).content,
            'html.parser'
        )
    )

def dynamic(url, driver:browser=None):
    """
    Open a webpage in a webdriver and return a soup of the contents
    """
    
    from bs4 import BeautifulSoup
    
    if driver is None:
        driver = browser()

    driver.open(url, True)

    return driver.soup()

def download(
    url: str,
    path: 'Path',
    show_progress: bool = True,
    cookies = None
):
    """
    Download file to disk
    """
    from tqdm import tqdm
    from urllib.request import urlretrieve

    r = get(
        url = url,
        stream = True,
        cookies = cookies
    )

    size = int(r.headers.get("content-length", 0))

    if show_progress:
        with tqdm(total=size, unit="B", unit_scale=True) as bar:
            with open(str(path), "wb") as file:
                for data in r.iter_content(1024):
                    bar.update(len(data))
                    file.write(data)
    else:
        urlretrieve(url, str(path))
