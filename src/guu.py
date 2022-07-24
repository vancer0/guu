from PyQt6.uic import loadUi
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QWidget, QApplication, QGroupBox, QLabel, QComboBox, QSplitter, QPushButton, QLineEdit, QPlainTextEdit, QProgressBar, QListWidget, QMenuBar, QMenu
import sys
import requests
import shutil
from webbrowser import open_new_tab
import os
from bs4 import BeautifulSoup
from configparser import RawConfigParser
import json
import libtorrent
from qbittorrentapi import Client as QBitClient

GUUVERSION = '0'

session = requests.Session() # Main web session

# Get directory of program
if getattr(sys, 'frozen', False):
    GUUPATH = sys._MEIPASS
else:
    GUUPATH = os.path.dirname(os.path.abspath(__file__))

LOGIN_STATUS = 0
CLIENT_STATUS = 0
GT_STATUS = 0


class Settings:
    global GUUPATH
    config_path = os.path.join(os.path.expanduser("~"), ".guu-config")

    try:
        config = RawConfigParser() 
        config.read(config_path)
    except:
        print("Unable to load config. Exiting.")
        sys.exit()
    else:
        print("Loaded config.")

    if not config.has_section('GENERAL'):
        config.add_section("GENERAL")
        config.set("GENERAL", "Language", "en")
    if not config.has_section('GAYTORRENT'):
        config.add_section("GAYTORRENT")
        config.set("GAYTORRENT", "SaveLogin", "0")
        config.set("GAYTORRENT", "GT_Username", "")
        config.set("GAYTORRENT", "GT_Password", "")
    if not config.has_section('CLIENT'):
        config.add_section("CLIENT")
        config.set("CLIENT", "AutoDL", "1")
        config.set("CLIENT", "Client", "qbittorrent")
        config.set("CLIENT", "WebUI_Host", 'localhost')
        config.set("CLIENT", "WebUI_Port", '8080')
        config.set("CLIENT", "WebUI_Username", 'admin')
        config.set("CLIENT", "WebUI_Password", '')
    if not config.has_section('UPLOADING'):
        config.add_section("UPLOADING")
        config.set("UPLOADING", "Save_Uploads", '0')
        config.set("UPLOADING", "Save_Path", '')

    with open(config_path, 'w') as config_file:
        config.write(config_file)

    language = config['GENERAL']['Language']

    savelgn = bool(int(config['GAYTORRENT']['SaveLogin']))
    gtusr = config['GAYTORRENT']['GT_Username']
    gtpwd = config['GAYTORRENT']['GT_Password']

    autodl = bool(int(config['CLIENT']['AutoDL']))
    client = config['CLIENT']['Client']
    webuiport = config['CLIENT']['WebUI_Port']
    webuihost = config['CLIENT']['WebUI_Host']
    webuiusr = config['CLIENT']['WebUI_Username']
    webuipwd = config['CLIENT']['WebUI_Password']

    saveupld = bool(int(config['UPLOADING']['Save_Uploads']))
    savepath = config['UPLOADING']['Save_Path']

    def save(language, savelgn, gtusr, gtpwd, autodl, client, webuiport, webuihost, webuiusr, webuipwd, saveupld, savepath):
        config_path = os.path.join(os.path.expanduser("~"), ".guu-config")
        if not Settings.config.has_section('GENERAL'):
            Settings.config.add_section("GENERAL")
        Settings.config.set("GENERAL", "Language", language)

        if not Settings.config.has_section('GAYTORRENT'):
            Settings.config.add_section("GAYTORRENT")
        Settings.config.set("GAYTORRENT", "SaveLogin", savelgn)
        Settings.config.set("GAYTORRENT", "GT_Username", gtusr)
        Settings.config.set("GAYTORRENT", "GT_Password", gtpwd)

        if not Settings.config.has_section('CLIENT'):
            Settings.config.add_section("CLIENT")
        Settings.config.set("CLIENT", "AutoDL", autodl)
        Settings.config.set("CLIENT", "Client", client)
        Settings.config.set("CLIENT", "WebUI_Host", webuihost)
        Settings.config.set("CLIENT", "WebUI_Port", webuiport)
        Settings.config.set("CLIENT", "WebUI_Username", webuiusr)
        Settings.config.set("CLIENT", "WebUI_Password", webuipwd)

        if not Settings.config.has_section('UPLOADING'):
            Settings.config.add_section("UPLOADING")
        Settings.config.set("UPLOADING", "Save_Uploads", saveupld)
        Settings.config.set("UPLOADING", "Save_Path", savepath)

        try:
            with open(config_path, 'w') as config_file:
                Settings.config.write(config_file)
        except:
            print("Unable to save config.")
        else:
            print("Config saved.")

    def login_save(savelgn, usr, pwd):
        config_path = os.path.join(os.path.expanduser("~"), ".guu-config")
        if not Settings.config.has_section('GAYTORRENT'):
            Settings.config.add_section("GAYTORRENT")
        Settings.config.set("GAYTORRENT", "SaveLogin", savelgn)
        Settings.config.set("GAYTORRENT", "GT_Username", usr)
        Settings.config.set("GAYTORRENT", "GT_Password", pwd)

        try:
            with open(config_path, 'w') as config_file:
                Settings.config.write(config_file)
        except:
            print("Unable to save config.")
        else:
            print("Config saved.")


class qBitTorrent:
    global CLIENT_STATUS
    if Settings.autodl == True:
        try:
            requests.get("http://" + Settings.webuihost + ":" + Settings.webuiport)
        except Exception:
            print("Client WebUI unreachable.")
            CLIENT_STATUS = 0
        else:
            print("Client WebUI found.")
            try:
                qbt_client = QBitClient(
                    host=Settings.webuihost, 
                    port=Settings.webuiport, 
                    username=Settings.webuiusr, 
                    password=Settings.webuipwd)
                qbt_client.auth_log_in()
            except Exception:
                print("Wrong WebUI credentials.")
                CLIENT_STATUS = 2
            else:
                print("Connection with client OK.")
                CLIENT_STATUS = 1


class Misc:
    # Open link in web browser
    def openlink(url):
        open_new_tab(url)
    
    # Create torrent
    def create_torrent(path, dirp):
        global GUUPATH
        try:
            fs = lt.file_storage()
            lt.add_files(fs, path)
            t = lt.create_torrent(fs)
            t.add_tracker("http://tracker.gaytor.rent:2710/announce", 0)
            t.set_creator('GayTor.rent Upload Utility v' + GUUVERSION)
            lt.set_piece_hashes(t, dirp)
            torrent = t.generate()    
            f = open(GUUPATH + '/.guucache/upl.torrent', "wb")
            f.write(lt.bencode(torrent))
            f.close()
        except:
            print("Failed while making torrent file. Exiting.")
            sys.exit()
        else:
            print("Created torrent OK.")

    # Check for updates
    def update_check():
        try:
            remote = requests.get("https://vancer0.github.io/guu/version.json", stream=True)
            data = json.loads(remote.text)
            ver = int(data["version"])
            return ver
        except:
            return 0

class Main(QMainWindow):
    def __init__(self):
        global GUUPATH
        super(Main, self).__init__()
        loadUi(GUUPATH + '/ui/gui.ui' ,self)

        self.actionNew.triggered.connect(self.wipe)
        self.actionOpen.triggered.connect(self.openproj)
        self.actionSave.triggered.connect(self.saveproj)
        self.actionExit.triggered.connect(lambda: sys.exit())
        self.actionOpen_WebUI.triggered.connect(self.openwebui)
        self.actionReload_categories.triggered.connect(self.categ_reload)
        self.actionPreferences.triggered.connect(self.open_settings)
        self.actionAbout.triggered.connect(self.open_about)
        self.dirpath = ''
        self.fldrSelBtn.clicked.connect(self.select_folder)
        self.fileSelBtn.clicked.connect(self.select_file)

        self.categories = ['Select Category', 'Amateur', 'Anal', 'Anime Games', 'Asian', 'Bareback', 'BDSM', 'Bears', 'Black', 'Books & Magazines', 'Chubbies', 'Clips', 'Comic & Yaoi', 'Daddies / Sons', 'Dildos', 'Fan Sites', 'Fetish', 'Fisting', 'Grey / Older', 'Group-Sex', 'Homemade', 'Hunks', 'Images', 'Interracial', 'Jocks', 'Latino', 'Mature', 'Media Programs', 'Member', 'Middle Eastern', 'Military', 'Oral-Sex', 'Softcore', 'Solo', 'Theamed Movie', 'Trans', 'TV / Episodes', 'Twinks', 'Vintage', 'Voyeur', 'Wrestling and Sports', 'Youngblood']
        self.subcategories = ['(Optional)', 'Amateur', 'Anal', 'Anime Games', 'Asian', 'Bareback', 'BDSM', 'Bears', 'Black', 'Books & Magazines', 'Chubbies', 'Clips', 'Comic & Yaoi', 'Daddies / Sons', 'Dildos', 'Fan Sites', 'Fetish', 'Fisting', 'Grey / Older', 'Group-Sex', 'Homemade', 'Hunks', 'Images', 'Interracial', 'Jocks', 'Latino', 'Mature', 'Media Programs', 'Member', 'Middle Eastern', 'Military', 'Oral-Sex', 'Softcore', 'Solo', 'Theamed Movie', 'Trans', 'TV / Episodes', 'Twinks', 'Vintage', 'Voyeur', 'Wrestling and Sports', 'Youngblood']
        self.categories_num = [0, 62, 29, 46, 30, 43, 19, 17, 44, 50, 9, 7, 48, 5, 67, 66, 34, 68, 27, 32, 63, 12, 33, 53, 57, 35, 36, 58, 37, 54, 38, 39, 56, 40, 45, 47, 1, 41, 42, 51, 65, 28]

        self.category.addItems(self.categories)
        self.category.activated.connect(self.enableitems)
        self.subcategory1.addItems(self.subcategories)
        self.subcategory2.addItems(self.subcategories)
        self.subcategory3.addItems(self.subcategories)
        self.subcategory4.addItems(self.subcategories)

        self.picn = 0
        self.addPicBtn.clicked.connect(self.add_pictures)
        self.rmPicBtn.clicked.connect(self.remove_pictures)

        self.uploadBtn.clicked.connect(self.uplchecks)

        self.loginBtn.clicked.connect(self.login)

        self.checks()

        ver = Misc.update_check()
        if ver == 0:
            QMessageBox.warning(self, 'GUU', "An error occured while checking for updates.")
            print("Cannot reach GitHub. Update check failed.")
        elif ver > int(GUUVERSION):
            choice = QMessageBox.question(self, 'GUU', "A new version of GUU is available. Do you want to download it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if choice == QMessageBox.StandardButton.Yes:
                Misc.openlink("https://github.com/vancer0/guu/releases/download/{}/GUU-{}-x86_64.AppImage".format(str(ver), str(ver)))
            else:
                pass
            print("New version available: {}".format(str(ver)))
        elif ver == int(GUUVERSION):
            print("No updates found.")
        else:
            print("Unknown error while checking updates.")
    
    #################
    # GUI FUNCTIONS #
    #################

    # Executes several checks to update the Status section, auto logs in if it is selected in the settings
    def checks(self):
        if Settings.savelgn == True:
            login_data = {'username': Settings.gtusr, 'password': Settings.gtpwd}
            r = session.post("https://www.gaytor.rent/takelogin.php", params = login_data)
            r = session.get("https://www.gaytor.rent/qtm.php")
            global LOGIN_STATUS
            if r.status_code == 200:
                LOGIN_STATUS = 1
                self.checklogin(Settings.gtusr)
            else:
                LOGIN_STATUS = 0
                self.checklogin('')
        else:
            self.checklogin('')

        global CLIENT_STATUS
        if CLIENT_STATUS == 1:
            self.statusLabel2.setText("qBitTorrent (Connected)")
        elif CLIENT_STATUS == 2:
            self.statusLabel2.setText("Invalid credentials")
        else:
            self.statusLabel2.setText("None")

        try:
            r = session.get('https://www.gaytor.rent')
            if r.status_code == 200:
                self.statusLabel4.setText("Online")
            else:
                self.statusLabel4.setText("Unreachable")
        except Exception:
            self.statusLabel4.setText("Unreachable")
    
    # Checks the login status for the Status section
    def checklogin(self, usr):
        if LOGIN_STATUS == 1:
            self.statusLabel6.clear()
            self.statusLabel6.setText(usr)
            self.loginBtn.setText("Log Out")
        elif LOGIN_STATUS == 0:
            self.statusLabel6.clear()
            self.statusLabel6.setText("Not logged in!")
            self.loginBtn.setText("Log In")
            self.loginBtn.clicked.connect(self.login)

    # Function to select a folder for the path
    def select_folder(self):
        folderpath = QFileDialog.getExistingDirectory(self, "Select Folder", "~")
        if folderpath:
            self.path.clear()
            self.path.insert(folderpath)
    
    # Function to select a file for the path
    def select_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Select File', '~',"All files (*.*)")
        if filepath:
            self.path.clear()
            self.path.insert(filepath[0])

    # Adds pictures to the list
    def add_pictures(self):
        filenames = QFileDialog.getOpenFileNames(self, 'Select Image(s)', '~',"Images (*.png *.jpg *.jpeg *.bmp *.tif *.psd)")
        if filenames:
            for pic in filenames[0]:
                self.picn = self.picn + 1
                #filesize = os.path.getsize(pic)
                #filesize_e = str(round((filesize / 1000000), 2)) + " MB"
                #self.model.appendRow([QStandardItem(str(self.picn)), QStandardItem(pic), QStandardItem(filesize_e)])
                self.picTable.addItem(pic)

    # Removes selected pictures from the list
    def remove_pictures(self):
        items = self.picTable.selectedIndexes()
        for i in range(len(items)):
            x = self.picTable.selectedIndexes()[0].row()
            self.picTable.takeItem(x)
    
    # Resets all inputs
    def wipe(self):
        choice = QMessageBox.question(self, 'New project', "Are you sure you want to start a new project?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            self.path.clear()
            self.category.setCurrentIndex(0)
            self.subcategory1.setCurrentIndex(0)
            self.subcategory2.setCurrentIndex(0)
            self.subcategory3.setCurrentIndex(0)
            self.subcategory4.setCurrentIndex(0)
            self.picTable.clear()
            self.title.clear()
            self.description.clear()
            self.enableitems()
            self.uploadStatus.setFormat('Waiting... (%p%)')
            self.uploadStatus.setValue(0)
        else:
            pass
    
    # Enables or disables the input widgets based on whether a main category is selected or not
    def enableitems(self):
        if self.category.currentIndex() == 0:
            self.subcategory1.setEnabled(False)
            self.subcategory2.setEnabled(False)
            self.subcategory3.setEnabled(False)
            self.subcategory4.setEnabled(False)
            self.addPicBtn.setEnabled(False)
            self.rmPicBtn.setEnabled(False)
            self.title.setEnabled(False)
            self.description.setEnabled(False)
            self.uploadBtn.setEnabled(False)
            self.picTable.setEnabled(False)
            self.uploadStatus.setEnabled(False)
        else:
            self.subcategory1.setEnabled(True)
            self.subcategory2.setEnabled(True)
            self.subcategory3.setEnabled(True)
            self.subcategory4.setEnabled(True)
            self.addPicBtn.setEnabled(True)
            self.rmPicBtn.setEnabled(True)
            self.title.setEnabled(True)
            self.description.setEnabled(True)
            self.uploadBtn.setEnabled(True)
            self.picTable.setEnabled(True)
            self.uploadStatus.setEnabled(True)
    
    # Pulls the category list from the website
    def categ_reload(self):
        # To Do
        QMessageBox.information(self, 'GUU', "Action not yet supported.")

    # Opens the torrent client's web UI
    def openwebui(self):
        global CLIENT_STATUS
        if CLIENT_STATUS == 0:
            QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please make sure it is running and try again.")
        elif CLIENT_STATUS == 2:
            QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please enter the correct credentials and try again.")
        else:
            Misc.openlink("http://" + Settings.webuihost + ':' + Settings.webuiport)
    
    #########################
    # ABOUT WINDOW FUNCTION #
    #########################

    # Opens about window
    def open_about(self):
        global GUUPATH
        self.aboutwin = QWidget()
        loadUi(GUUPATH + '/ui/about.ui', self.aboutwin)
        self.aboutwin.show()
        global GUUVERSION
        self.aboutwin.label.setText('<html><head/><body><p><span style=\" font-size:18pt;\">Gaytor.rent Upload Utility v' + GUUVERSION + '</span></p></body></html>')
        self.aboutwin.label_4.linkActivated.connect(lambda: Misc.openlink("https://www.gnu.org/licenses/gpl-3.0-standalone.html"))
        self.aboutwin.label_8.linkActivated.connect(lambda: Misc.openlink("https://github.com/psf/requests"))
        self.aboutwin.label_9.linkActivated.connect(lambda: Misc.openlink("https://www.crummy.com/software/BeautifulSoup"))
        self.aboutwin.label_10.linkActivated.connect(lambda: Misc.openlink("https://github.com/arvidn/libtorrent"))
        self.aboutwin.label_11.linkActivated.connect(lambda: Misc.openlink("https://github.com/rmartin16/qbittorrent-api"))

    #############################
    # SETTINGS WINDOW FUNCTIONS #
    #############################
    
    # Opens settings window
    def open_settings(self):
        global GUUPATH
        self.setwin = QWidget()
        loadUi(GUUPATH + '/ui/settings.ui', self.setwin)
        self.setwin.show()
        self.setwin.autoLogin.setChecked(Settings.savelgn)
        self.setwin.autoLogin.stateChanged.connect(self.set_enablegt)
        self.setwin.gtUsername.setText(Settings.gtusr)
        self.setwin.gtPassword.setText(Settings.gtpwd)
        self.setwin.autoDl.setChecked(Settings.autodl)
        self.setwin.autoDl.stateChanged.connect(self.set_enableclient)
        self.setwin.webuiHost.setText(Settings.webuihost)
        self.setwin.webuiPort.setText(Settings.webuiport)
        self.setwin.webuiUser.setText(Settings.webuiusr)
        self.setwin.webuiPwd.setText(Settings.webuipwd)
        self.setwin.saveUploads.setChecked(Settings.saveupld)
        self.setwin.saveUploads.stateChanged.connect(self.set_enabledl)
        self.setwin.savePath.setText(Settings.savepath)
        self.setwin.saveSetBtn.clicked.connect(self.save_settings)
        self.setwin.saveSetBtn.setShortcut("Return")
        self.set_enablegt()
        self.set_enableclient()
    
    # Enables or disables the client input widgets based on whether auto seeding is enabled or not
    def set_enableclient(self):
        if self.setwin.autoDl.isChecked() == True:
            self.setwin.torrentClient.setEnabled(True)
            self.setwin.webuiHost.setEnabled(True)
            self.setwin.webuiPort.setEnabled(True)
            self.setwin.webuiUser.setEnabled(True)
            self.setwin.webuiPwd.setEnabled(True)
        else:
            self.setwin.torrentClient.setEnabled(False)
            self.setwin.webuiHost.setEnabled(False)
            self.setwin.webuiPort.setEnabled(False)
            self.setwin.webuiUser.setEnabled(False)
            self.setwin.webuiPwd.setEnabled(False)
    
    # Enables or disables the gaytor.rent input widgets based on whether saving credentials is enabled or not
    def set_enablegt(self):
        if self.setwin.autoLogin.isChecked() == True:
            self.setwin.gtUsername.setEnabled(True)
            self.setwin.gtPassword.setEnabled(True)
        else:
            self.setwin.gtUsername.setEnabled(False)
            self.setwin.gtPassword.setEnabled(False)
    
    # Enables or disables the download widgets based on whether it is enabled or not
    def set_enabledl(self):
        if self.setwin.saveUploads.isChecked() == True:
            self.setwin.savePath.setEnabled(True)
            self.setwin.savePathBrowse.setEnabled(True)
        else:
            self.setwin.savePath.setEnabled(False)
            self.setwin.savePathBrowse.setEnabled(False)
    
    # Sends all the input values to the settings class to be saved
    def save_settings(self):
        language = "en"
        savelgn = int(self.setwin.autoLogin.isChecked())
        gtusr = self.setwin.gtUsername.text()
        gtpwd = self.setwin.gtPassword.text()
        autodl = int(self.setwin.autoDl.isChecked())
        client = "qbittorrent"
        webuihost = self.setwin.webuiHost.text()
        webuiport = self.setwin.webuiPort.text()
        webuiusr = self.setwin.webuiUser.text()
        webuipwd = self.setwin.webuiPwd.text()
        saveupld = int(self.setwin.saveUploads.isChecked())
        savepath = self.setwin.savePath.text()

        Settings.save(language, savelgn, gtusr, gtpwd, autodl, client, webuiport, webuihost, webuiusr, webuipwd, saveupld, savepath)

        self.setwin.close()
        QMessageBox.information(self, 'GUU', "Please restart the program for the changes to take effect.")
    
    #######################
    # UPLOADING FUNCTIONS #
    #######################
    
    # Executes several checks to ensure that the user can proceed to uploading
    def uplchecks(self):
        choice = QMessageBox.question(self, 'GUU', "Are you sure you want to upload?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            global CLIENT_STATUS
            global LOGIN_STATUS
            if Settings.autodl == True:
                if CLIENT_STATUS == 0:
                    QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please make sure it is running and try again.")
                elif CLIENT_STATUS == 2:
                    QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please enter the correct credentials and try again.")
                else:
                    if LOGIN_STATUS == 1:
                        self.uploadmanager()
                    else:
                        QMessageBox.warning(self, 'GUU', "Please log in to Gaytor.rent before uploading.")
            else:
                if LOGIN_STATUS == 1:
                    self.uploadmanager()
                else:
                    QMessageBox.warning(self, 'GUU', "Please log in to Gaytor.rent before uploading.")
    
    # Controlls the several upload functions according to the user settings
    def uploadmanager(self):
        global GUUPATH

        self.mc = self.categories_num[self.category.currentIndex()]
        self.sc1 = self.categories_num[self.subcategory1.currentIndex()]
        self.sc2 = self.categories_num[self.subcategory2.currentIndex()]
        self.sc3 = self.categories_num[self.subcategory3.currentIndex()]
        self.sc4 = self.categories_num[self.subcategory4.currentIndex()]

        self.tor_title_var = self.title.text()
        self.tor_desc_var = self.description.toPlainText()
        self.path_var = self.path.text()
        self.dirpath = os.path.dirname(self.path.text())

        self.piclist = []
        piccount = self.picTable.count()
        for line in range(piccount):
            value = self.picTable.item(line).text()
            self.piclist.insert(piccount, value)
            piccount = piccount - 1

        self.upload()

        if Settings.saveupld == True:
            self.download()
            try:
                shutil.copy(GUUPATH + '/.guucache/dl.torrent', '"' + os.dirname(Settings.savepath + '/') + '/' + self.tor_title_var + '.torrent"')
            except shutil.SameFileError:
                QMessageBox.warning(self, 'GUU', "Torrent already exists in the download folder.")
            except PermissionError:
                QMessageBox.warning(self, 'GUU', "You do not have permission to save the torrent in the selected download folder.")
            except:
                QMessageBox.warning(self, 'GUU', "An error occured while saving the torrent.")

        if Settings.autodl == True:
            if Settings.webuihost == "localhost" or Settings.webuihost == "127.0.0.1":
                self.dlpath = self.dirpath
                self.seed()
                shutil.rmtree(GUUPATH + '/.guucache')
                self.uploadStatus.setFormat('Done! (%p%)')
                self.uploadStatus.setValue(8)
                QMessageBox.information(self, 'GUU', "Upload complete!")
            else:
                self.dlwin = QWidget()
                loadUi(GUUPATH + '/ui/dlselect.ui', self.dlwin)
                self.dlwin.show()
                def get():
                    self.dlpath = self.dlwin.remotePath.text()
                    self.dlwin.close()
                    self.seed()
                    shutil.rmtree(GUUPATH + '/.guucache')
                    self.uploadStatus.setFormat('Done! (%p%)')
                    self.uploadStatus.setValue(8)
                    QMessageBox.information(self, 'GUU', "Upload complete!")
                self.dlwin.okBtn.clicked.connect(get)
                self.dlwin.remotePath.setText(self.dirpath)
        else:
            shutil.rmtree(GUUPATH + '/.guucache')
            self.uploadStatus.setFormat('Done! (%p%)')
            self.uploadStatus.setValue(8)
            QMessageBox.information(self, 'GUU', "Upload complete!")
    
    # Uploads the torrent
    def upload(self):
        global GUUPATH
        url = "https://www.gaytor.rent/doupload.php"

        self.uploadStatus.setFormat('Creating torrent file... (%p%)')
        self.uploadStatus.setValue(1)
        # Try to create the cache folder
        try:
            os.mkdir(GUUPATH + '/.guucache')
        except Exception:
            shutil.rmtree(GUUPATH + '/.guucache')
            os.mkdir(GUUPATH + '/.guucache')

        # Create torrent
        Misc.create_torrent(self.path_var, self.dirpath)

        self.uploadStatus.setFormat('Uploading pictures... (%p%)')
        self.uploadStatus.setValue(2)

        # Upload pictures
        piccount = len(self.piclist)
        try:
            for pic in self.piclist:
                pics = {'ulpic[]': open(pic, 'rb')}
                r = session.post(url, files=pics)
        except:
            print("Failed while uploading pictures. Aborting upload.")
            return
        else:
            print("Uploaded pictures OK.")
        
        self.uploadStatus.setFormat('Gathering picture IDs... (%p%)')
        self.uploadStatus.setValue(3)

        # Get picture IDs
        pidlist = []
        def getdata(url): 
            r = session.get(url) 
            return r.text
        htmldata = getdata(url) 
        soup = BeautifulSoup(htmldata, 'html.parser') 
        for item in soup.find_all('img'):
            tmp = item["src"]
            if tmp.startswith('/tpics') == True:
                pid = tmp[15:tmp.rfind(".")]
                pidlist.insert(piccount, pid)
        print("Gathered picture IDs OK.")
        
        self.uploadStatus.setFormat('Uploading torrent... (%p%)')
        self.uploadStatus.setValue(4)

        # Gather upload data
        upload_data = {'MAX_FILE_SIZE': 40000000, 'type': self.mc, 'scat1': self.sc1, 'scat2': self.sc2, 'scat3': self.sc3, 'scat4': self.sc4, 'ulpic[]': '', 'name': self.tor_title_var, 'infourl': '', 'descr': self.tor_desc_var, 'checktorrent': 'Do it!'}
        tor_file = {'file': open(GUUPATH + '/.guucache/upl.torrent', 'rb')}

        # Add picture IDs to upload data
        for pid in pidlist:
            uplpic_id = 'uplpic' + pid
            upload_data[uplpic_id] = pid
        
        # Upload the data
        try:
            r = session.post(url, data = upload_data, files = tor_file) # Post upload data
        except:
            print("Failed while uploading torrent. Aborting upload.")
            return
        else:
            print("Uploaded data OK.")

        # Get the uploaded torrent's URL send it to the download function
        self.tor_url = r.url
    
    # Downloads the uploaded torrent
    def download(self):
        global GUUPATH
        self.uploadStatus.setFormat('Getting torrent ID... (%p%)')
        self.uploadStatus.setValue(5)
        tor_id = self.tor_url[41:89] # Get torrent ID
        urle = "https://www.gaytor.rent/download.php/" + tor_id + "/dl.torrent" # Create the download link
        
        self.uploadStatus.setFormat('Downloading torrent... (%p%)')
        self.uploadStatus.setValue(6)

        # Download the torrent and save it as dl.torrent
        try:
            with session.get(urle) as r:
                with open(GUUPATH + '/.guucache/dl.torrent', 'wb') as f:
                    for chunk in r.iter_content(chunk_size = 16*1024):
                        f.write(chunk)
        except:
            print("Failed while downloading torrent. Aborting download.")
            return
        else:
            print("Downloaded torrent OK.")
    
    # Adds the downloaded torrent to the torrent client for seeding
    def seed(self):
        global GUUPATH
        self.uploadStatus.setFormat('Adding torrent to the client... (%p%)')
        self.uploadStatus.setValue(7)
        try:
            qBitTorrent.qbt_client.torrents_add(torrent_files=GUUPATH + '/.guucache/dl.torrent', savepath=self.dlpath, is_paused=False)
        except:
            print("Failed while adding torrent to the client.")
            return
        else:
            print("Added torrent to client OK.")

    ###################
    # LOGIN FUNCTIONS #
    ###################
    
    # Opens login window if user is not logged in, logs out if user is logged in.
    def login(self):
        global LOGIN_STATUS
        if LOGIN_STATUS == 0:
            self.logwin = QWidget()
            loadUi(GUUPATH + '/ui/login.ui', self.logwin)
            self.logwin.show()
            self.logwin.logwinBtn.clicked.connect(self.sendlogin)
            self.logwin.logwinBtn.setShortcut("Return")
        else:
            try:
                r = session.get("https://www.gaytor.rent/logout.php")
            except:
                LOGIN_STATUS = 0
            else:
                LOGIN_STATUS = 0
            self.checklogin('')
    
    # Sends login credentials to the website for authentication
    def sendlogin(self):
        usr = self.logwin.username.text()
        pwd = self.logwin.password.text()

        login_data = {'username': usr, 'password': pwd} 
        try:
            r = session.post("https://www.gaytor.rent/takelogin.php", params = login_data) 
        except:
            print("Failed to login.")
            QMessageBox.warning(self, 'GUU', "Login failed!")
        else:
            print("Logged in OK.")

        global LOGIN_STATUS
        try:
            r = session.get("https://www.gaytor.rent/qtm.php")
            if r.status_code == 200:
                LOGIN_STATUS = 1
            else:
                LOGIN_STATUS = 0
        except Exception:
            LOGIN_STATUS = 0

        if LOGIN_STATUS == 1:
            if self.logwin.credSave.isChecked() == True:
                savelgn = int(self.logwin.credSave.isChecked())
                Settings.login_save(savelgn, usr, pwd)
            self.logwin.close()
            self.checklogin(usr)
        else:
            QMessageBox.warning(self, 'GUU', "Login failed!")
    
    ######################
    # PROJECTS FUNCTIONS #
    ######################
    
    # Clears input widgets and loads the selected project file
    def openproj(self):
        filename = QFileDialog.getOpenFileName(self, 'Open Project', '~',"GUU Files (*.guu)")
        if filename == ('', ''):
            return
        else:
            f = open(str(filename[0]))

        try:
            data = json.load(f)
        except:
            print("Failed while loading project.")
            QMessageBox.warning(self, 'GUU', "An error occured while opening the project.")
            return

        self.category.setCurrentIndex(data["Categories"]["Main"])
        self.enableitems()
        self.path.clear()
        self.path.setText(data["Info"]["Path"])
        self.subcategory1.setCurrentIndex(data["Categories"]["Secondary1"])
        self.subcategory2.setCurrentIndex(data["Categories"]["Secondary2"])
        self.subcategory3.setCurrentIndex(data["Categories"]["Secondary3"])
        self.subcategory4.setCurrentIndex(data["Categories"]["Secondary4"])
        self.title.clear()
        self.title.setText(data["Info"]["Title"])
        self.description.clear()
        self.description.insertPlainText(data["Info"]["Description"])
        self.picTable.clear()
        self.tmp = 0
        for pic in data["Pictures"]["Path(s)"]:
            try:
                self.tmp = self.tmp + 1
                self.picTable.addItem(pic)
            except FileNotFoundError:
                QMessageBox.warning(self, 'GUU', pic + " was not found.")
        self.uploadStatus.setValue(0)
        self.uploadStatus.setFormat('Waiting... (%p%)')
        print("Loaded project OK.")
    
    # Saves all input values to a project file
    def saveproj(self):
        mc = self.category.currentIndex()
        sc1 = self.subcategory1.currentIndex()
        sc2 = self.subcategory2.currentIndex()
        sc3 = self.subcategory3.currentIndex()
        sc4 = self.subcategory4.currentIndex()

        tor_title_var = self.title.text()
        tor_desc_var = self.description.toPlainText()
        path_var = self.path.text()

        piclist = []
        piccount = self.picTable.count()
        for line in range(piccount):
            value = self.picTable.item(line).text()
            piclist.insert(piccount, value)
            piccount = piccount - 1

        saveas = QFileDialog.getSaveFileName(self, 'Save File', 'Untitled.guu', "GUU Files (*.guu)")

        if saveas is None:
            return
        else:
            data = {}
            data['Categories'] = {"Main": mc, "Secondary1": sc1, "Secondary2": sc2, "Secondary3": sc3, "Secondary4": sc4}
            data['Info'] = {"Title": tor_title_var, "Description": tor_desc_var, "Path": path_var}
            data['Pictures'] = {"Path(s)": piclist}
            i = saveas[0]
            if i[len(i)-4:len(i)] == ".guu":
                filename = saveas[0]
            else:
                filename = saveas[0] + ".guu"

            try:
                with open(filename, 'w') as f:
                    json.dump(data, f)
            except:
                print("Failed while saving project.")
            else:
                print("Saved project OK.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()

    try:
        sys.exit(app.exec())
    except:
        pass
