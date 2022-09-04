from PyQt6.uic import loadUi
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QWidget, QApplication, QGroupBox, QLabel, QComboBox, QSplitter, QPushButton, QLineEdit, QPlainTextEdit, QProgressBar, QListWidget, QMenuBar, QMenu
import sys
import shutil
import os
import json
from json import JSONDecodeError
import qdarktheme

from settings import Settings
from misc import Misc
from constants import version, themes, torrent_clients, languages
from api import GayTorrent


class Main(QMainWindow):
    def __init__(self):
        global GUUPATH
        super(Main, self).__init__()
        loadUi(os.path.join(GUUPATH, "ui", "gui.ui"), self)
        print("GUU: Drawing window")

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

        self.load_categs()

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

        self.update_check()

    #################
    # GUI FUNCTIONS #
    #################

    # Executes several checks to update the Status section, auto logs in if it
    # is selected in the settings
    def checks(self):
        api.check_server_status()
        if api.server_status == 0:
            self.statusLabel4.setText("Unreachable")
            self.checklogin('')
        else:
            self.statusLabel4.setText("Online")

            if cfg.savelgn:
                api.send_login_data(cfg.gtusr, cfg.gtpwd)
                api.check_login_status()

                if api.login_status == 1:
                    print("GUU: Auto login OK")
                    self.checklogin(cfg.gtusr)
                    self.categ_reload()
                else:
                    print("GUU: Auto login failed")
                    self.checklogin('')
            else:
                self.checklogin('')

        if client.status == 1:
            self.statusLabel2.setText("{} (Connected)".format(cfg.client))
        elif client.status == 2:
            self.statusLabel2.setText("Invalid credentials")
        else:
            self.statusLabel2.setText("None")

    # Checks the login status for the Status section
    def checklogin(self, usr):
        if api.login_status == 1:
            self.statusLabel6.clear()
            self.statusLabel6.setText(usr)
            self.loginBtn.setText("Log Out")
        elif api.login_status == 0:
            self.statusLabel6.clear()
            self.statusLabel6.setText("Not logged in!")
            self.loginBtn.setText("Log In")
            self.loginBtn.clicked.connect(self.login)

    # Check for updates
    def update_check(self):
        v = Misc.update_link()
        if v[0] == 1:
            choice = QMessageBox.question(self, 'GUU', "A new version of GUU is available. Do you want to download it?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if choice == QMessageBox.StandardButton.Yes:
                Misc.openlink(v[1])
            else:
                return
        else:
            return

    # Function to select a folder for the path
    def select_folder(self):
        folderpath = QFileDialog.getExistingDirectory(
            self, "Select Folder", "~")
        if folderpath:
            self.path.clear()
            self.path.insert(folderpath)

    # Function to select a file for the path
    def select_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Select File', '~',
                                               "All files (*.*)")
        if filepath:
            self.path.clear()
            self.path.insert(filepath[0])

    # Adds pictures to the list
    def add_pictures(self):
        filenames = QFileDialog.getOpenFileNames(self, 'Select Image(s)', '~',
                                                 "Images (*.png *.jpg *.jpeg *.bmp *.tif *.psd)")
        if filenames:
            for pic in filenames[0]:
                self.picn = self.picn + 1
                # filesize = os.path.getsize(pic)
                # filesize_e = str(round((filesize / 1000000), 2)) + " MB"
                # self.model.appendRow([QStandardItem(str(self.picn)), QStandardItem(pic), QStandardItem(filesize_e)])
                self.picTable.addItem(pic)

    # Removes selected pictures from the list
    def remove_pictures(self):
        items = self.picTable.selectedIndexes()
        for i in range(len(items)):
            x = self.picTable.selectedIndexes()[0].row()
            self.picTable.takeItem(x)

    # Resets all inputs
    def wipe(self):
        choice = QMessageBox.question(self, 'New project', "Are you sure you want to start a new project?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
            print("GUU: Cleared all fields")
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

    # Loads categories from file
    def load_categs(self):
        categ_path = os.path.join(cfg.data_path, "categories.cache")

        if os.path.exists(categ_path):
            print("GUU: Category cache exists")
            self.categories = ["Select Category"]
            self.subcategories = ["(Optional)"]
            self.categories_num = [0]
            with open(categ_path, 'r') as f:
                try:
                    c = json.load(f)
                except JSONDecodeError:
                    os.remove(categ_path)
                    print("GUU: Category cache does not exist")
                    self.categories = ["Log in to load categories"]
                    self.subcategories = ["Log in to load categories"]
                    self.categories_num = [0]
                    return
                else:
                    for key in c:
                        self.categories.append(key)
                        self.subcategories.append(key)
                        self.categories_num.append(c[key])
            print("GUU: Loaded categories from cache")
        else:
            print("GUU: Category cache does not exist")
            self.categories = ["Log in to load categories"]
            self.subcategories = ["Log in to load categories"]
            self.categories_num = [0]

    # Pulls the category list from the website
    def categ_reload(self):
        if api.login_status == 1:
            c = api.fetch_categories()

            self.categories = ["Select Category"]
            self.subcategories = ["(Optional)"]
            self.categories_num = [0]

            for key in c:
                self.categories.append(key)
                self.subcategories.append(key)
                self.categories_num.append(c[key])

            self.category.clear()
            self.subcategory1.clear()
            self.subcategory2.clear()
            self.subcategory3.clear()
            self.subcategory4.clear()

            self.category.addItems(self.categories)
            self.subcategory1.addItems(self.subcategories)
            self.subcategory2.addItems(self.subcategories)
            self.subcategory3.addItems(self.subcategories)
            self.subcategory4.addItems(self.subcategories)

            print("GUU: Loaded categories from server")

            categ_path = os.path.join(cfg.data_path, "categories.cache")
            with open(categ_path, 'w') as f:
                json.dump(c, f)
                f.close()
            print("GUU: Categories saved to cache")
        else:
            QMessageBox.warning(
                self,
                'GUU',
                "You must be logged in to download the category list.")

    # Opens the torrent client's web UI
    def openwebui(self):
        if client.status == 0:
            QMessageBox.warning(
                self,
                'GUU',
                "Cannot communicate with the torrent client. Please make sure it is running and try again.")
        elif client.status == 2:
            QMessageBox.warning(
                self,
                'GUU',
                "Cannot communicate with the torrent client. Please enter the correct credentials and try again.")
        else:
            Misc.openlink("http://" + cfg.webuihost +
                          ':' + cfg.webuiport)

    #########################
    # ABOUT WINDOW FUNCTION #
    #########################

    # Opens about window
    def open_about(self):
        global GUUPATH
        self.aboutwin = QWidget()
        loadUi(GUUPATH + '/ui/about.ui', self.aboutwin)
        self.aboutwin.show()
        self.aboutwin.label.setText(
            '<html><head/><body><p><span style=\" font-size:18pt;\">Gaytor.rent Upload Utility v' + version + '</span></p></body></html>')
        self.aboutwin.label_4.linkActivated.connect(lambda: Misc.openlink(
            "https://www.gnu.org/licenses/gpl-3.0-standalone.html"))
        self.aboutwin.label_8.linkActivated.connect(
            lambda: Misc.openlink("https://github.com/psf/requests"))
        self.aboutwin.label_9.linkActivated.connect(
            lambda: Misc.openlink("https://www.crummy.com/software/BeautifulSoup"))
        self.aboutwin.label_10.linkActivated.connect(
            lambda: Misc.openlink("https://github.com/arvidn/libtorrent"))
        self.aboutwin.label_11.linkActivated.connect(
            lambda: Misc.openlink("https://github.com/rmartin16/qbittorrent-api"))
        self.aboutwin.label_5.linkActivated.connect(
            lambda: Misc.openlink("https://github.com/5yutan5/PyQtDarkTheme"))

    #############################
    # SETTINGS WINDOW FUNCTIONS #
    #############################

    # Opens settings window
    def open_settings(self):
        global GUUPATH
        self.setwin = QWidget()
        loadUi(GUUPATH + '/ui/settings.ui', self.setwin)
        self.setwin.show()
        self.setwin.language.addItems(languages)
        self.setwin.language.setCurrentIndex(languages.index(cfg.language))
        self.setwin.theme.setCurrentIndex(themes.index(cfg.theme))
        self.setwin.autoLogin.setChecked(cfg.savelgn)
        self.setwin.autoLogin.stateChanged.connect(self.set_enablegt)
        self.setwin.gtUsername.setText(cfg.gtusr)
        self.setwin.gtPassword.setText(cfg.gtpwd)
        self.setwin.autoDl.setChecked(cfg.autodl)
        self.setwin.autoDl.stateChanged.connect(self.set_enableclient)
        self.setwin.torrentClient.addItems(torrent_clients)
        self.setwin.torrentClient.setCurrentIndex(torrent_clients.index(cfg.client))
        self.setwin.webuiHost.setText(cfg.webuihost)
        self.setwin.webuiPort.setText(cfg.webuiport)
        self.setwin.webuiUser.setText(cfg.webuiusr)
        self.setwin.webuiPwd.setText(cfg.webuipwd)
        self.setwin.saveUploads.setChecked(cfg.saveupld)
        self.setwin.saveUploads.stateChanged.connect(self.set_enabledl)
        self.setwin.savePath.setText(cfg.savepath)
        self.setwin.savePathBrowse.clicked.connect(self.select_save_folder)
        self.setwin.saveSetBtn.clicked.connect(self.save_settings)
        self.setwin.saveSetBtn.setShortcut("Return")
        self.set_enablegt()
        self.set_enableclient()
        self.set_enabledl()

    # Selects the auto save path
    def select_save_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Folder")
        if path:
            self.setwin.savePath.clear()
            self.setwin.savePath.insert(path)

    # Enables or disables the client input widgets based on whether auto seeding is enabled or not
    def set_enableclient(self):
        if self.setwin.autoDl.isChecked():
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
        if self.setwin.autoLogin.isChecked():
            self.setwin.gtUsername.setEnabled(True)
            self.setwin.gtPassword.setEnabled(True)
        else:
            self.setwin.gtUsername.setEnabled(False)
            self.setwin.gtPassword.setEnabled(False)

    # Enables or disables the download widgets based on whether it is enabled or not
    def set_enabledl(self):
        if self.setwin.saveUploads.isChecked():
            self.setwin.savePath.setEnabled(True)
            self.setwin.savePathBrowse.setEnabled(True)
        else:
            self.setwin.savePath.setEnabled(False)
            self.setwin.savePathBrowse.setEnabled(False)

    # Sends all the input values to the settings class to be saved
    def save_settings(self):
        language = languages[self.setwin.language.currentIndex()]
        theme = themes[self.setwin.theme.currentIndex()]
        savelgn = int(self.setwin.autoLogin.isChecked())
        gtusr = self.setwin.gtUsername.text()
        gtpwd = self.setwin.gtPassword.text()
        autodl = int(self.setwin.autoDl.isChecked())
        client = torrent_clients[self.setwin.torrentClient.currentIndex()]
        webuihost = self.setwin.webuiHost.text()
        webuiport = self.setwin.webuiPort.text()
        webuiusr = self.setwin.webuiUser.text()
        webuipwd = self.setwin.webuiPwd.text()
        saveupld = int(self.setwin.saveUploads.isChecked())
        savepath = self.setwin.savePath.text()

        cfg.save(language, theme, savelgn, gtusr, gtpwd, autodl, client,
                 webuiport, webuihost, webuiusr, webuipwd, saveupld, savepath)

        self.setwin.close()
        QMessageBox.information(
            self, 'GUU', "Please restart the program for the changes to take effect.")

    #######################
    # UPLOADING FUNCTIONS #
    #######################

    # Executes several checks to ensure that the user can proceed to uploading
    def uplchecks(self):
        self.uploadStatus.setMaximum(0)
        choice = QMessageBox.question(self,
                                      'GUU',
                                      "Are you sure you want to upload?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            if cfg.autodl:
                if client.status == 0:
                    QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please make sure it is running and try again.")
                    self.uploadStatus.setMaximum(1)
                elif client.status == 2:
                    QMessageBox.warning(self, 'GUU', "Cannot communicate with the torrent client. Please enter the correct credentials and try again.")
                    self.uploadStatus.setMaximum(1)
                else:
                    if api.login_status == 1:
                        self.uploadmanager()
                    else:
                        QMessageBox.warning(self, 'GUU', "Please log in to Gaytor.rent before uploading.")
                        self.uploadStatus.setMaximum(1)
            else:
                if api.login_status == 1:
                    self.uploadmanager()
                else:
                    QMessageBox.warning(self, 'GUU', "Please log in to Gaytor.rent before uploading.")
                    self.uploadStatus.setMaximum(1)

    # Controls the several upload functions according to the user settings
    def uploadmanager(self):
        global GUUPATH

        mc = self.categories_num[self.category.currentIndex()]
        sc1 = self.categories_num[self.subcategory1.currentIndex()]
        sc2 = self.categories_num[self.subcategory2.currentIndex()]
        sc3 = self.categories_num[self.subcategory3.currentIndex()]
        sc4 = self.categories_num[self.subcategory4.currentIndex()]

        tor_title_var = self.title.text()
        tor_desc_var = self.description.toPlainText()
        path_var = self.path.text()
        dirpath = os.path.dirname(self.path.text())

        piclist = []
        piccount = self.picTable.count()
        for line in range(piccount):
            value = self.picTable.item(line).text()
            piclist.insert(piccount, value)
            piccount = piccount - 1

        tor_url = api.upload(path_var,
                             dirpath,
                             piclist,
                             mc,
                             sc1,
                             sc2,
                             sc3,
                             sc4,
                             tor_title_var,
                             tor_desc_var)

        print(tor_url)

        if cfg.saveupld:
            tor_path = api.download(tor_url)
            try:
                shutil.copy(tor_path,
                            os.path.join(os.path.dirname(cfg.savepath + '/'),
                                         tor_title_var + '.torrent'))
            except shutil.SameFileError:
                QMessageBox.warning(
                    self, 'GUU', "Torrent already exists in the download folder.")
            except PermissionError:
                QMessageBox.warning(
                    self, 'GUU', "You do not have permission to save the torrent in the selected download folder.")
            else:
                print("GUU: Torrent saved")

        if cfg.autodl:
            if cfg.webuihost == "localhost" or cfg.webuihost == "127.0.0.1":
                self.dlpath = self.dirpath
                tor_path = api.download(tor_url)
                client.add_torrent(tor_path, self.dlpath)
                shutil.rmtree(api.temp_path)
                self.uploadStatus.setMaximum(1)
                QMessageBox.information(self, 'GUU', "Upload complete!")
            else:
                self.dlwin = QWidget()
                loadUi(os.path.join(GUUPATH, "ui", "dlselect.ui"), self.dlwin)
                self.dlwin.show()

                def get():
                    self.dlpath = self.dlwin.remotePath.text()
                    self.dlwin.close()
                    tor_path = api.download(tor_url)
                    client.add_torrent(tor_path, self.dlpath)
                    shutil.rmtree(api.temp_path)
                    self.uploadStatus.setMaximum(1)
                    QMessageBox.information(self, 'GUU', "Upload complete!")
                self.dlwin.okBtn.clicked.connect(get)
                self.dlwin.remotePath.setText(self.dirpath)
        else:
            shutil.rmtree(api.temp_path)
            self.uploadStatus.setMaximum(1)
            QMessageBox.information(self, 'GUU', "Upload complete!")

    ###################
    # LOGIN FUNCTIONS #
    ###################

    # Opens login window if user is not logged in, logs out if user is logged in.
    def login(self):
        if api.login_status == 0:
            self.logwin = QWidget()
            loadUi(os.path.join(GUUPATH, "ui," "login.ui"), self.logwin)
            self.logwin.show()
            self.logwin.logwinBtn.clicked.connect(self.sendlogin)
            self.logwin.logwinBtn.setShortcut("Return")
        elif api.login_status == 1:
            api.logout()
            self.checklogin('')

    # Sends login credentials to the website for authentication
    def sendlogin(self):
        usr = self.logwin.username.text()
        pwd = self.logwin.password.text()

        api.send_login_data(usr, pwd)

        api.check_login_status()

        if api.login_status == 1:
            if self.logwin.credSave.isChecked():
                savelgn = int(self.logwin.credSave.isChecked())
                cfg.login_save(savelgn, usr, pwd)
            self.categ_reload()
            self.logwin.close()
            self.checklogin(usr)
        else:
            QMessageBox.warning(self, 'GUU', "Login failed!")

    ######################
    # PROJECTS FUNCTIONS #
    ######################

    # Clears input widgets and loads the selected project file
    def openproj(self):
        filename = QFileDialog.getOpenFileName(self, 'Open Project', '~',
                                               "GUU Files (*.guu)")
        if filename == ('', ''):
            return
        else:
            f = open(str(filename[0]))

        data = json.load(f)

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
        print("GUU: Loaded project OK.")

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

        saveas = QFileDialog.getSaveFileName(self, 'Save File', 'Untitled.guu',
                                             "GUU Files (*.guu)")

        if saveas is None:
            return
        else:
            data = {}
            data['Categories'] = {"Main": mc,
                                  "Secondary1": sc1,
                                  "Secondary2": sc2,
                                  "Secondary3": sc3,
                                  "Secondary4": sc4}
            data['Info'] = {"Title": tor_title_var,
                            "Description": tor_desc_var,
                            "Path": path_var}
            data['Pictures'] = {"Path(s)": piclist}
            i = saveas[0]
            if i[len(i)-4:len(i)] == ".guu":
                filename = saveas[0]
            else:
                filename = saveas[0] + ".guu"

            with open(filename, 'w') as f:
                json.dump(data, f)
            print("GUU: Saved project OK.")


if __name__ == '__main__':
    api = GayTorrent()

    if getattr(sys, 'frozen', False):
        GUUPATH = sys._MEIPASS
    else:
        GUUPATH = os.path.dirname(os.path.abspath(__file__))

    GT_STATUS = 0

    cfg = Settings()

    client = Misc.select_client(cfg)

    app = QApplication(sys.argv)
    win = Main()

    if cfg.theme == "system":
        app.setStyleSheet("")
    elif cfg.theme == "dark":
        app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    elif cfg.theme == "light":
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))

    win.show()

    sys.exit(app.exec())
