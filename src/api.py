import requests
import os
import shutil
import sys
from requests import Timeout, ConnectionError
from bs4 import BeautifulSoup
import jwt


class GayTorrent:
    def __init__(self, log):
        self.session = requests.Session()
        self.login_status = 0
        self.server_status = 0
        self.username = ""
        self.get_temp_path()

        self.log = log

    def get_temp_path(self):
        # Find temp folder
        if sys.platform.startswith('linux'):
            self.temp_path = os.path.join(os.path.expanduser("~"),
                                          ".cache",
                                          "gaytorrent")
        elif sys.platform.startswith('win'):
            self.temp_path = os.path.join(os.path.expanduser("~"),
                                          "AppData",
                                          "Local",
                                          "Temp",
                                          "gaytorrent")
        elif sys.platform.startswith('darwin'):
            self.temp_path = os.path.join(os.path.expanduser("~"),
                                          "Library",
                                          "Caches",
                                          "TemporaryItems",
                                          "gaytorrent")
        else:
            self.temp_path = os.path.join(os.path.expanduser("~"),
                                          ".cache",
                                          "gaytorrent")

    # Check if server if online and changes the server_status
    # variable accordingly
    def check_server_status(self):
        try:
            r = self.session.head('https://www.gaytor.rent', timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            self.server_status = 0
        else:
            if r.status_code == 200:
                self.server_status = 1
            else:
                self.server_status = 0

    # Sends the provided username and password to the
    # server for authentication.
    def login(self, username: str, password: str):
        login_data = {'username': username, 'password': password}
        try:
            self.session.post("https://www.gaytor.rent/takelogin.php",
                              params=login_data, timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
        self.get_username()

    # Checks whether the user is logged in or not and changes
    # the login_status variable accordingly
    def check_login_status(self):
        try:
            r = self.session.head("https://www.gaytor.rent/qtm.php", timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            self.login_status = 0
        else:
            if r.status_code == 200:
                self.log.new(1, 2, "Logged in OK.")
                self.login_status = 1
            else:
                self.login_status = 0

    # Logs out
    def logout(self):
        try:
            self.session.get("https://www.gaytor.rent/logout.php", timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
        else:
            self.login_status = 0

    # Fetches the categories from the server and returns
    # a dictionary with the names and IDs
    def fetch_categories(self):
        self.log.new(1, 2, "Fetching category list")
        try:
            r = self.session.get(
                "https://www.gaytor.rent/genrelist.php",
                timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            return
        categories = {}
        raw = str(r.text)[46:].split('\n')
        for c in raw:
            if c != '':
                b = c.split(";")
                categories[b[1]] = b[0]
        return categories

    # Uploads a torrent
    def upload(self, tor_path: str, piclist: [str], mc: str, sc1: str,
               sc2: str, sc3: str, sc4: str, tor_title: str, tor_desc: str):
        url = "https://www.gaytor.rent/doupload.php"

        # Upload pictures
        piccount = len(piclist)
        try:
            for pic in piclist:
                pics = {'ulpic[]': open(pic, 'rb')}
                self.session.post(url, files=pics, timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            return
        else:
            self.log.new(1, 2, "Uploaded pictures OK.")

        # Get picture IDs
        pidlist = []

        def getdata(url):
            try:
                r = self.session.get(url, timeout=60)
            except(Timeout, ConnectionError):
                self.log.new(2, 2, "Failed to connect to server")
            return r.text
        htmldata = getdata(url)
        soup = BeautifulSoup(htmldata, 'html.parser')
        for item in soup.find_all('img'):
            tmp = item["src"]
            if tmp.startswith('/tpics'):
                pid = tmp[15:tmp.rfind(".")]
                pidlist.insert(piccount, pid)
        self.log.new(1, 2, "Gathered picture IDs OK.")

        # Gather upload data
        upload_data = {'MAX_FILE_SIZE': 40000000,
                       'type': mc,
                       'scat1': sc1,
                       'scat2': sc2,
                       'scat3': sc3,
                       'scat4': sc4,
                       'ulpic[]': '',
                       'name': tor_title,
                       'infourl': '',
                       'descr': tor_desc,
                       'checktorrent': 'Do it!'}
        tor_file = {'file': open(tor_path, 'rb')}

        # Add picture IDs to upload data
        for pid in pidlist:
            uplpic_id = 'uplpic' + pid
            upload_data[uplpic_id] = pid

        # Upload the data
        try:
            r = self.session.post(url,
                                  data=upload_data,
                                  files=tor_file,
                                  timeout=60)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            return
        else:
            self.log.new(1, 2, "Uploaded data OK.")
            # Return the uploaded torrent's URL
            return r.url

    # Downloads a torrent from a given URL and returns the file path
    def download(self, tor_url: str):
        tor_id = tor_url[39:87]  # Get torrent ID
        urle = "https://www.gaytor.rent/download.php/" + tor_id + "/dl.torrent"

        # Download the torrent and save it as dl.torrent
        dest = os.path.join(self.temp_path, "dl.torrent")
        try:
            with self.session.get(urle, timeout=60) as r:
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=16*1024):
                        f.write(chunk)
        except(Timeout, ConnectionError):
            self.log.new(2, 2, "Failed to connect to server")
            return
        else:
            self.log.new(1, 2, "Downloaded torrent OK.")
            return dest

    # Gets the username
    def get_username(self):
        token = self.session.cookies.get_dict()["token"]
        token_dec = jwt.decode(token, "secret", algorithms=["HS256"],
                               options={'verify_signature': False})
        self.username = token_dec["username"]
