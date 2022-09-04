from webbrowser import open_new_tab
import libtorrent as lt
import json
import requests
import sys

from constants import version
from clients import QBitTorrent


class Misc:
    # Open link in web browser
    def openlink(url):
        print("GUU: Opening {}".format(str(url)))
        open_new_tab(url)

    # Create torrent
    def create_torrent(path, dirp, dest):
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

        print("GUU: Created torrent OK.")

    # Checks for updates and returns DL link
    def update_link():
        try:
            remote = requests.get("https://vancer0.github.io/guu/version.json",
                                  stream=True, timeout=3)
            data = json.loads(remote.text)
            ver = int(data["version"])
        except Exception:
            ver = 0

        if ver == 0:
            print("GUU: Cannot reach GitHub. Update check failed.")
            return [0, ""]
        elif ver > int(version):
            print("GUU: New version available: {}".format(str(ver)))
            if sys.platform.startswith('linux'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Linux-x86_64.AppImage"]
            elif sys.platform.startswith('win'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Win-x86_64.exe"]
            elif sys.platform.startswith('darwin'):
                return [1, "https://github.com/vancer0/guu/releases/latest/download/GUU-Mac-x86_64.dmg"]
            else:
                return [1, "https://github.com/vancer0/guu/releases/tag/{}".format(str(ver))]
        elif ver == int(version):
            print("GUU: No updates found.")
            return [0, ""]
        else:
            print("GUU: Unknown error while checking updates.")
            return [0, ""]

    # Sets the torrent client
    def select_client(cfg):
        # if cfg.client == "qBitTorrent":
        return QBitTorrent(cfg)
