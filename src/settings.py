import sys
import os
from configparser import RawConfigParser

from constants import config_defaults


class Settings:
    def __init__(self):
        self.get_data_path()

        self.config_path = os.path.join(self.data_path, "config")
        self.config = RawConfigParser()

        self.load_config()
        self.generate()

        self.compatibility()

    # Define path
    def get_data_path(self):
        if sys.platform.startswith('linux'):
            self.data_path = os.path.join(os.path.expanduser("~"),
                                          ".config",
                                          "guu")
        elif sys.platform.startswith('win'):
            self.data_path = os.path.join(os.path.expanduser("~"),
                                          "AppData",
                                          "Roaming",
                                          "guu")
        elif sys.platform.startswith('darwin'):
            self.data_path = os.path.join(os.path.expanduser("~"),
                                          "Library",
                                          "Preferences",
                                          "guu")
        else:
            self.data_path = os.path.join(os.path.expanduser("~"),
                                          ".config",
                                          "guu")

        os.makedirs(self.data_path, exist_ok=True)

    # Loads the config
    def load_config(self):
        self.config.read(self.config_path)

        self.language = self.config['GENERAL']['Language']
        self.theme = self.config['GENERAL']['Theme']
        self.savelgn = bool(int(self.config['GAYTORRENT']['SaveLogin']))
        self.gtusr = self.config['GAYTORRENT']['GT_Username']
        self.gtpwd = self.config['GAYTORRENT']['GT_Password']
        self.autodl = bool(int(self.config['CLIENT']['AutoDL']))
        self.client = self.config['CLIENT']['Client']
        self.webuiport = self.config['CLIENT']['WebUI_Port']
        self.webuihost = self.config['CLIENT']['WebUI_Host']
        self.webuiusr = self.config['CLIENT']['WebUI_Username']
        self.webuipwd = self.config['CLIENT']['WebUI_Password']
        self.saveupld = bool(int(self.config['UPLOADING']['Save_Uploads']))
        self.savepath = self.config['UPLOADING']['Save_Path']

        print("GUU: Loaded config.")

    # Generates the config
    def generate(self):
        for section in config_defaults:
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option in config_defaults[section]:
                if option not in self.config[section]:
                    self.config.set(section, option, config_defaults[section][option])

        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)

    # Saves given values to the config
    def save(self, language, theme, savelgn, gtusr, gtpwd, autodl, client,
             webuiport, webuihost, webuiusr, webuipwd, saveupld, savepath):
        self.generate()

        self.config.set("GENERAL", "Language", language)
        self.config.set("GENERAL", "Theme", theme)

        self.config.set("GAYTORRENT", "SaveLogin", savelgn)
        self.config.set("GAYTORRENT", "GT_Username", gtusr)
        self.config.set("GAYTORRENT", "GT_Password", gtpwd)

        self.config.set("CLIENT", "AutoDL", autodl)
        self.config.set("CLIENT", "Client", client)
        self.config.set("CLIENT", "WebUI_Host", webuihost)
        self.config.set("CLIENT", "WebUI_Port", webuiport)
        self.config.set("CLIENT", "WebUI_Username", webuiusr)
        self.config.set("CLIENT", "WebUI_Password", webuipwd)

        self.config.set("UPLOADING", "Save_Uploads", saveupld)
        self.config.set("UPLOADING", "Save_Path", savepath)

        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)

        print("GUU: Config saved.")

    # Saves only the login credentials
    def login_save(self, savelgn, usr, pwd):
        self.generate()

        self.config.set("GAYTORRENT", "SaveLogin", savelgn)
        self.config.set("GAYTORRENT", "GT_Username", usr)
        self.config.set("GAYTORRENT", "GT_Password", pwd)

        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)
        print("GUU: Config saved.")

    # Converts the config from previous formats to work on the latest version
    def compatibility(self):
        if self.client == "qbittorrent":
            self.config.set("CLIENT", "client", "qBitTorrent")
            with open(self.config_path, 'w') as config_file:
                self.config.write(config_file)
            print("GUU: Config converted")
            self.load_config()
