from qbittorrentapi import Client as QBitClient
import requests
from requests.exceptions import Timeout, ConnectionError


class QBitTorrent:
    def __init__(self, cfg):
        try:
            requests.head("http://" + cfg.webuihost +
                          ":" + cfg.webuiport, timeout=3)
        except(Timeout, ConnectionError):
            print("CLT: QBitTorrent WebUI unreachable.")
            self.status = 0
        else:
            print("CLT: QBitTorrent WebUI found.")
            try:
                self.client = QBitClient(
                    host=cfg.webuihost,
                    port=cfg.webuiport,
                    username=cfg.webuiusr,
                    password=cfg.webuipwd)
                self.client.auth_log_in()
            except Exception:
                print("CLT: Wrong QBitTorrent WebUI credentials.")
                self.status = 2
            else:
                print("CLT: Connection with QBitTorrent OK.")
                self.status = 1

    def add_torrent(self, path, dlpath):
        self.client.torrents_add(
            torrent_files=path, savepath=dlpath, is_paused=False)
        print("CLT: Added torrent to client OK.")
