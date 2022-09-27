from qbittorrentapi import Client as QBitClient
import requests
from requests.exceptions import Timeout, ConnectionError


class QBitTorrent:
    def __init__(self, log, cfg):
        self.log = log

        try:
            requests.head("http://" + cfg.webuihost +
                          ":" + cfg.webuiport, timeout=3)
        except(Timeout, ConnectionError):
            self.log.new(2, 3, "QBitTorrent WebUI unreachable.")
            self.status = 0
        else:
            self.log.new(1, 3, "QBitTorrent WebUI found.")
            if cfg.autodl:
                try:
                    self.client = QBitClient(
                        host=cfg.webuihost,
                        port=cfg.webuiport,
                        username=cfg.webuiusr,
                        password=cfg.webuipwd)
                    self.client.auth_log_in()
                except:
                    self.log.new(2, 3, "Wrong QBitTorrent WebUI credentials.")
                    self.status = 2
                else:
                    self.log.new(1, 3, "Connection with QBitTorrent OK.")
                    self.status = 1
            else:
                self.status = 0

    def add_torrent(self, path: str, dlpath: str):
        self.client.torrents_add(
            torrent_files=path, savepath=dlpath, is_paused=False)
        self.log.new(1, 3, "Added torrent to client OK.")
