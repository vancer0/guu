from webbrowser import open_new_tab
import libtorrent as lt
import json
import requests
from requests import Timeout, ConnectionError
import sys
import os

from constants import version
from clients import QBitTorrent


class Misc:
    def __init__(self, log):
        self.log = log

    # Open link in web browser
    def openlink(self, url: str):
        self.log.new(1, 1, "Opening {}".format(str(url)))
        open_new_tab(url)

    # Create torrent
    def create_torrent(self, path: str, dirp: str, dest: str):
        fs = lt.file_storage()
        lt.add_files(fs, path)
        t = lt.create_torrent(fs)
        t.add_tracker("http://tracker.gaytor.rent:2710/announce", 0)
        t.set_creator("GayTor.rent Upload Utility v" + version)
        lt.set_piece_hashes(t, dirp)
        torrent = t.generate()
        with open(dest, "wb") as f:
            f.write(lt.bencode(torrent))
            f.close()

        self.log.new(1, 1, "Created torrent OK.")

    # Checks for updates and returns DL link
    def update_link(self):
        try:
            remote = requests.get("https://vancer0.github.io/guu/version.json",
                                  stream=True, timeout=3)
            data = json.loads(remote.text)
            ver = int(data["version"])
        except Exception:
            ver = 0

        if ver == 0:
            self.log.new(2, 1, "Cannot reach GitHub. Update check failed.")
            return [0, ""]
        elif ver > int(version):
            self.log.new(1, 1, "New version available: {}".format(str(ver)))
            if sys.platform.startswith('linux'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Linux-x86_64.AppImage"]
            elif sys.platform.startswith('win'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Win-x86_64.exe"]
            elif sys.platform.startswith('darwin'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Mac-x86_64.dmg"]
            else:
                return [1, "https://github.com/vancer0/guu/releases/tag/{}".format(str(ver))]
        elif ver == int(version):
            self.log.new(1, 1, "No updates found.")
            return [0, ""]
        else:
            self.log.new(2, 1, "Unknown error while checking updates.")
            return [0, ""]

    # Sets the torrent client
    def select_client(self, cfg):
        # if cfg.client == "qBitTorrent":
        return QBitTorrent(self.log, cfg)

    # Downloads all available language packs to cache
    def fetch_lang_packs(self, folder: str):
        try:
            remote = requests.get("https://vancer0.github.io/guu/languages.json",
                                  stream=True,
                                  timeout=3)
        except (Timeout, ConnectionError):
            self.log.new(2, 1, "Failed to download language packs")
            return self.use_offline_lang_packs(folder)
        else:
            data = json.loads(remote.text)

        lang = []

        for language in data:
            lang.append(data[language])

        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

        for language in lang:
            url = "https://vancer0.github.io/guu/languages/{}.json".format(language)
            try:
                remote = requests.get(url,
                                      stream=True,
                                      timeout=3)
            except (Timeout, ConnectionError):
                self.log.new(2, 1, "Failed to download language: {}".format(language))
                break
            else:
                lang_data = remote.text

            path = os.path.join(folder, "{}.json".format(language))
            if os.path.exists(path):
                os.remove(path)
            with open(path, "w") as f:
                f.write(lang_data)
                f.close()
            self.log.new(1, 1, "Downloaded language: {}".format(language))

        return self.use_offline_lang_packs(folder)

    def use_offline_lang_packs(self, folder: str):
        if not os.path.exists(folder):
            return [], []
        else:
            file_list = []
            for filename in os.listdir(folder):
                f = os.path.join(folder, filename)
                if os.path.isfile(f):
                    if f[-4:] == "json":
                        file_list.append(f)

            lang = []
            lang_full = []

            for filename in file_list:
                f = json.load(open(filename, 'r'))

                lang.append(os.path.basename(filename)[:-5])
                lang_full.append(f["language"])

            return lang, lang_full
