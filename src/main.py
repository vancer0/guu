from PyQt6.uic import loadUi
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QWidget, QApplication, QGroupBox, QLabel, QComboBox, QSplitter, QPushButton, QLineEdit, QPlainTextEdit, QProgressBar, QMenuBar, QMenu
from PyQt6.QtCore import QSize, QObject, pyqtSignal, QThread, pyqtSlot
import sys
import shutil
import os
import json
from json import JSONDecodeError
import qdarktheme
import traceback

from settings import Settings
from misc import Misc
from constants import version, themes, torrent_clients
from api import GayTorrent
from language import Language
from qt_classes import GUUClasses
from crash_report import CrashReport
from logger import GUULogging
from misc import Misc


class UploadManager(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    # Controls the several upload functions according to the user settings
    @pyqtSlot()
    def run(self, path, dirpath, piclist, mc, sc1, sc2,
            sc3, sc4, tor_title_var, tor_desc_var):
        # Try to create the cache folder
        try:
            os.mkdir(api.temp_path)
        except Exception:
            shutil.rmtree(api.temp_path)
            os.mkdir(api.temp_path)

        self.progress.emit("Creating torrent...")
        log.new(1, 1, "Creating torrent")
        dest = os.path.join(api.temp_path, "upl.torrent")
        misc.create_torrent(path, dirpath, dest)

        self.progress.emit("Uploading torrent...")
        log.new(1, 1, "Sending torrent to API for upload")
        tor_url = api.upload(dest,
                             piclist,
                             mc,
                             sc1,
                             sc2,
                             sc3,
                             sc4,
                             tor_title_var,
                             tor_desc_var)

        if cfg.saveupld:
            tor_path = api.download(tor_url)
            self.progress.emit("Saving torrent...")
            try:
                shutil.copy(tor_path,
                            os.path.join(os.path.dirname(cfg.savepath + '/'),
                                         tor_title_var + '.torrent'))
            except shutil.SameFileError:
                QMessageBox.warning(
                    self, 'GUU', lang.popups.torrent_dl_already_exists)
            except PermissionError:
                QMessageBox.warning(
                    self, 'GUU', lang.popups.torrent_dl_no_permission)
            else:
                log.new(1, 1, "Torrent saved")

        if cfg.autodl:
            self.progress.emit("Adding torrent to client...")
            if cfg.webuihost == "localhost" or cfg.webuihost == "127.0.0.1":
                self.dlpath = dirpath
                tor_path = api.download(tor_url)
                client.add_torrent(tor_path, self.dlpath)
                shutil.rmtree(api.temp_path)
                self.finished.emit()
            else:
                win.dlwin.show()

                def get():
                    self.dlpath = win.dlwin.remotePath.text()
                    win.dlwin.close()
                    tor_path = api.download(tor_url)
                    client.add_torrent(tor_path, self.dlpath)
                    shutil.rmtree(api.temp_path)
                    self.finished.emit()
                win.dlwin.okBtn.clicked.connect(get)
                win.dlwin.remotePath.setText(dirpath)
        else:
            shutil.rmtree(api.temp_path)
            self.finished.emit()


class Main(QMainWindow):
    def __init__(self, parent=None):
        global GUUPATH
        super(Main, self).__init__()

        sys.modules['GUUClasses'] = GUUClasses

        log.new(1, 1, "Drawing window")
        loadUi(os.path.join(GUUPATH, "ui", "gui.ui"), self)

        log.new(1, 1, "Loading widgets")
        self.logwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "login.ui"), self.logwin)
        self.dlwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "dlselect.ui"), self.dlwin)
        self.aboutwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "about.ui"), self.aboutwin)
        self.setwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "settings.ui"), self.setwin)
        self.uplwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "upload.ui"), self.uplwin)
        self.crashwin = QWidget()
        loadUi(os.path.join(GUUPATH, "ui", "crash-widget.ui"), self.crashwin)

        self.set_lang()

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

        self.picTable.setIconSize(QSize(150, 150))
        self.addPicBtn.clicked.connect(self.select_pictures)
        self.rmPicBtn.clicked.connect(self.remove_pictures)

        self.uploadBtn.clicked.connect(self.uplchecks)

        self.loginBtn.clicked.connect(self.login)

        self.checks()

        self.update_check()

    def closeEvent(self, event):
        self.close_all()

    def close_all(self):
        self.close()
        if self.uplwin:
            self.uplwin.close()
        if self.setwin:
            self.setwin.close()
        if self.aboutwin:
            self.aboutwin.close()
        if self.logwin:
            self.logwin.close()

    #################
    # GUI FUNCTIONS #
    #################

    # Changes all text to this from the language file
    def set_lang(self):
        self.menuFile.setTitle(lang.ui.file)
        self.actionExit.setText(lang.ui.exit)
        self.actionNew.setText(lang.ui.new)
        self.actionOpen.setText(lang.ui.open)
        self.actionSave.setText(lang.ui.save)

        self.menuTools.setTitle(lang.ui.tools)
        self.actionOpen_WebUI.setText(lang.ui.open_webui)
        self.actionPreferences.setText(lang.ui.preferences)
        self.actionReload_categories.setText(lang.ui.reload_categories)

        self.menuHelp.setTitle(lang.ui.help)
        self.actionAbout.setText(lang.ui.about)

        self.fileBox.setTitle(lang.ui.file)
        self.pathLabel.setText(lang.ui.path)
        self.fldrSelBtn.setText(lang.ui.select_folder)
        self.fileSelBtn.setText(lang.ui.select_file)

        self.categoriesBox.setTitle(lang.ui.categories)
        self.catLabel.setText(lang.ui.category)
        self.sc1Label.setText(lang.ui.subcategory1)
        self.sc2Label.setText(lang.ui.subcategory2)
        self.sc3Label.setText(lang.ui.subcategory3)
        self.sc4Label.setText(lang.ui.subcategory4)

        self.picturesBox.setTitle(lang.ui.pictures)
        self.addPicBtn.setText(lang.ui.add_pictures)
        self.rmPicBtn.setText(lang.ui.remove_pictures)

        self.infoBox.setTitle(lang.ui.info)
        self.titleLabel.setText(lang.ui.title)
        self.descLabel.setText(lang.ui.description)
        self.uploadStatus.setFormat(lang.ui.waiting)
        self.uploadBtn.setText(lang.ui.upload)

        self.statusBox.setTitle(lang.ui.status)
        self.statusLabel1.setText(lang.ui.torrent_client)
        self.statusLabel5.setText(lang.ui.user)
        self.loginBtn.setText(lang.ui.login)

    # Executes several checks to update the Status section, auto logs in if it
    # is selected in the settings
    def checks(self):
        api.check_server_status()
        if api.server_status == 0:
            self.statusLabel4.setText(lang.ui.unreachable)
            self.checklogin()
        else:
            self.statusLabel4.setText(lang.ui.online)

            if cfg.savelgn:
                api.login(cfg.gtusr, cfg.gtpwd)
                api.check_login_status()

                if api.login_status == 1:
                    log.new(1, 1, "Auto login OK")
                    self.checklogin()
                    self.categ_reload()
                else:
                    log.new(2, 1, "Auto login failed")
                    self.checklogin()
            else:
                self.checklogin()

        if client.status == 1:
            self.statusLabel2.setText("{} ({})".format(cfg.client,
                                                       lang.ui.connected))
        elif client.status == 2:
            self.statusLabel2.setText(lang.ui.invalid_credentials)
        else:
            self.statusLabel2.setText(lang.ui.none)

    # Checks the login status for the Status section
    def checklogin(self):
        if api.login_status == 1:
            self.statusLabel6.clear()
            self.statusLabel6.setText(api.username)
            self.loginBtn.setText(lang.ui.logout)
        elif api.login_status == 0:
            self.statusLabel6.clear()
            self.statusLabel6.setText(lang.ui.not_logged_in)
            self.loginBtn.setText(lang.ui.login)
            self.loginBtn.clicked.connect(self.login)

    # Check for updates
    def update_check(self):
        v = misc.update_link()
        if v[0] == 1:
            choice = QMessageBox.question(self, 'GUU', lang.popups.new_version,
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if choice == QMessageBox.StandardButton.Yes:
                misc.openlink(v[1])
            else:
                return
        else:
            return

    # Function to select a folder for the path
    def select_folder(self):
        folderpath = QFileDialog.getExistingDirectory(
            self, lang.ui.select_folder)
        if folderpath:
            self.path.clear()
            self.path.insert(folderpath)

    # Function to select a file for the path
    def select_file(self):
        filepath = QFileDialog.getOpenFileName(self, lang.ui.select_file, '',
                                               "All files (*.*)")
        if filepath:
            self.path.clear()
            self.path.insert(filepath[0])

    # File dialog to select pictures
    def select_pictures(self):
        filenames = QFileDialog.getOpenFileNames(self,
                                                 lang.file_dialogs.select_images,
                                                 '',
                                                 "Images (*.png *.jpg *.jpeg *.bmp *.tif *.psd)")
        if filenames:
            self.picTable.add_pictures(filenames[0])

    # Removes selected pictures from the list
    def remove_pictures(self):
        items = self.picTable.selectedIndexes()
        for i in range(len(items)):
            x = self.picTable.selectedIndexes()[0].row()
            self.picTable.takeItem(x)

    # Resets all inputs
    def wipe(self):
        choice = QMessageBox.question(self, 'New project', lang.popups.new_project_confirm,
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
            log.new(1, 1, "Category cache exists")
            self.categories = [lang.ui.select_category]
            self.subcategories = [lang.ui.optional]
            self.categories_num = [0]
            with open(categ_path, 'r') as f:
                try:
                    c = json.load(f)
                except JSONDecodeError:
                    f.close()
                    os.remove(categ_path)
                    log.new(2, 1, "Category cache does not exist")
                    self.categories = [lang.ui.categories_login_error]
                    self.subcategories = [lang.ui.categories_login_error]
                    self.categories_num = [0]
                    return
                else:
                    for key in c:
                        self.categories.append(key)
                        self.subcategories.append(key)
                        self.categories_num.append(c[key])
            log.new(1, 1, "Loaded categories from cache")
        else:
            log.new(2, 1, "Category cache does not exist")
            self.categories = [lang.ui.categories_login_error]
            self.subcategories = [lang.ui.categories_login_error]
            self.categories_num = [0]

    # Pulls the category list from the website
    def categ_reload(self):
        if api.login_status == 1:
            c = api.fetch_categories()

            self.categories = [lang.ui.select_category]
            self.subcategories = [lang.ui.optional]
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

            log.new(1, 1, "Loaded categories from server")

            categ_path = os.path.join(cfg.data_path, "categories.cache")
            with open(categ_path, 'w') as f:
                json.dump(c, f)
                f.close()
            log.new(1, 1, "Categories saved to cache")
        else:
            QMessageBox.warning(
                self,
                'GUU',
                lang.popups.categories_fetch_login_error)

    # Opens the torrent client's web UI
    def openwebui(self):
        if client.status == 0:
            QMessageBox.warning(
                self,
                'GUU',
                lang.popups.client_not_running)
        elif client.status == 2:
            QMessageBox.warning(
                self,
                'GUU',
                lang.popups.client_wrong_credentials)
        else:
            misc.openlink("http://" + cfg.webuihost +
                          ':' + cfg.webuiport)

    #########################
    # ABOUT WINDOW FUNCTION #
    #########################

    # Opens about window
    def open_about(self):
        global GUUPATH
        self.aboutwin.show()
        self.set_about_lang()
        self.aboutwin.label.setText(
            "<html><head/><body><p><span style=\" font-size:18pt;\">{} v{}</span></p></body></html>".format(lang.about.guu, version))
        self.aboutwin.label_4.linkActivated.connect(lambda: misc.openlink(
            "https://www.gnu.org/licenses/gpl-3.0-standalone.html"))
        self.aboutwin.label_8.linkActivated.connect(
            lambda: misc.openlink("https://github.com/psf/requests"))
        self.aboutwin.label_9.linkActivated.connect(
            lambda: misc.openlink("https://www.crummy.com/software/BeautifulSoup"))
        self.aboutwin.label_10.linkActivated.connect(
            lambda: misc.openlink("https://github.com/arvidn/libtorrent"))
        self.aboutwin.label_11.linkActivated.connect(
            lambda: misc.openlink("https://github.com/rmartin16/qbittorrent-api"))
        self.aboutwin.label_5.linkActivated.connect(
            lambda: misc.openlink("https://github.com/5yutan5/PyQtDarkTheme"))

    # Changes all text to this from the language file
    def set_about_lang(self):
        self.aboutwin.label_2.setText('<html><head/><body><p><span style=" font-size:12pt;">{}</span></p></body></html>'.format(lang.about.made_by.format("vancer")))
        self.aboutwin.label_3.setText(lang.about.license)
        self.aboutwin.label_4.setText('<html><head/><body><p><a href="https://www.gnu.org/licenses/gpl-3.0-standalone.html"><span style=" text-decoration: underline; color:#e9643a;">{}</span></a></p></body></html>'.format(lang.about.view_license))
        self.aboutwin.label_7.setText(lang.about.libraries_used)

    #############################
    # SETTINGS WINDOW FUNCTIONS #
    #############################

    # Opens settings window
    def open_settings(self):
        global GUUPATH
        self.setwin.show()
        self.set_settings_lang()
        self.setwin.language.addItems(languages_full)
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

    # Changes all text to this from the language file
    def set_settings_lang(self):
        self.setwin.setWindowTitle("GUU - {}".format(lang.settings.settings))

        self.setwin.groupBox.setTitle(lang.settings.general)
        self.setwin.languageLabel.setText(lang.settings.language)
        self.setwin.themeLabel.setText(lang.settings.theme)

        self.setwin.autoLogin.setText(lang.settings.auto_login)
        self.setwin.gtuserLabel.setText(lang.settings.username)
        self.setwin.gtpasswdLabel.setText(lang.settings.password)
        self.setwin.label_2.setText(lang.settings.credentials_warning)

        self.setwin.clientBox.setTitle(lang.settings.client)
        self.setwin.autoDl.setText(lang.settings.auto_seed)
        self.setwin.clientLabel.setText(lang.settings.torrent_client)
        self.setwin.hostLabel.setText(lang.settings.webui_host)
        self.setwin.portLabel.setText(lang.settings.webui_port)
        self.setwin.userLabel.setText(lang.settings.webui_username)
        self.setwin.pwdLabel.setText(lang.settings.webui_password)

        self.setwin.uploadingBox.setTitle(lang.settings.uploading)
        self.setwin.saveUploads.setText(lang.settings.save_torrents)
        self.setwin.savePathBrowse.setText(lang.settings.browse)

        self.setwin.saveSetBtn.setText(lang.settings.save)

    # Selects the auto save path
    def select_save_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, lang.ui.select_folder)
        if path:
            self.setwin.savePath.clear()
            self.setwin.savePath.insert(path)

    # Enables or disables the client input widgets based on
    # whether auto seeding is enabled or not
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

    # Enables or disables the gaytor.rent input widgets based on
    # whether saving credentials is enabled or not
    def set_enablegt(self):
        if self.setwin.autoLogin.isChecked():
            self.setwin.gtUsername.setEnabled(True)
            self.setwin.gtPassword.setEnabled(True)
        else:
            self.setwin.gtUsername.setEnabled(False)
            self.setwin.gtPassword.setEnabled(False)

    # Enables or disables the download widgets based on
    # whether it is enabled or not
    def set_enabledl(self):
        if self.setwin.saveUploads.isChecked():
            self.setwin.savePath.setEnabled(True)
            self.setwin.savePathBrowse.setEnabled(True)
        else:
            self.setwin.savePath.setEnabled(False)
            self.setwin.savePathBrowse.setEnabled(False)

    # Sends all the input values to the settings class to be saved
    # and reloads the config
    def save_settings(self):
        global client, languages, languages_full, lang

        set_language = languages[self.setwin.language.currentIndex()]
        set_theme = themes[self.setwin.theme.currentIndex()]
        set_savelgn = int(self.setwin.autoLogin.isChecked())
        set_gtusr = self.setwin.gtUsername.text()
        set_gtpwd = self.setwin.gtPassword.text()
        set_autodl = int(self.setwin.autoDl.isChecked())
        set_client = torrent_clients[self.setwin.torrentClient.currentIndex()]
        set_webuihost = self.setwin.webuiHost.text()
        set_webuiport = self.setwin.webuiPort.text()
        set_webuiusr = self.setwin.webuiUser.text()
        set_webuipwd = self.setwin.webuiPwd.text()
        set_saveupld = int(self.setwin.saveUploads.isChecked())
        set_savepath = self.setwin.savePath.text()

        cfg.save(set_language, set_theme, set_savelgn, set_gtusr, set_gtpwd,
                 set_autodl, set_client, set_webuiport, set_webuihost,
                 set_webuiusr, set_webuipwd, set_saveupld, set_savepath)

        cfg.load_config()
        if cfg.autodl:
            client = misc.select_client(cfg)
        else:
            client.logout()
        self.set_lang()
        self.load_categs()
        self.checks()
        languages, languages_full = misc.fetch_lang_packs(
            os.path.join(cfg.data_path, "languages"))
        if languages == []:
            from constants import languages, languages_full
            lang = Language(cfg.language,
                            os.path.join(GUUPATH, "languages"))
        else:
            lang = Language(cfg.language,
                            os.path.join(cfg.data_path, "languages"))
        if cfg.theme == "system":
            app.setStyleSheet("")
        elif cfg.theme == "dark":
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
        elif cfg.theme == "light":
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))

        self.setwin.close()

    #######################
    # UPLOADING FUNCTIONS #
    #######################

    # Executes several checks to ensure that the user can proceed to uploading
    def uplchecks(self):
        self.uploadStatus.setMaximum(0)
        choice = QMessageBox.question(self,
                                      'GUU',
                                      lang.popups.upload_confirm,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            if cfg.autodl:
                if client.status == 0:
                    QMessageBox.warning(self,
                                        'GUU',
                                        lang.popups.client_not_running)
                    self.uploadStatus.setMaximum(1)
                elif client.status == 2:
                    QMessageBox.warning(self,
                                        'GUU',
                                        lang.popups.client_wrong_credentials)
                    self.uploadStatus.setMaximum(1)
                else:
                    if api.login_status == 1:
                        self.upload()
                    else:
                        QMessageBox.warning(self,
                                            'GUU',
                                            lang.popups.upload_login_error)
                        self.uploadStatus.setMaximum(1)
            else:
                if api.login_status == 1:
                    self.upload()
                else:
                    QMessageBox.warning(self,
                                        'GUU',
                                        lang.popups.upload_login_error)
                    self.uploadStatus.setMaximum(1)

    # Calls the upload functions on a separate thread
    def upload(self):
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
            piclist.append(value)
            # piclist.insert(piccount, value)
            # piccount = piccount - 1

        self.uplwin.show()

        thread = QThread(parent=self)
        worker = UploadManager()
        worker.moveToThread(thread)

        thread.started.connect(lambda: worker.run(path_var, dirpath, piclist, mc, sc1, sc2, sc3, sc4, tor_title_var, tor_desc_var))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self.uploadStatus.setMaximum(1))
        thread.finished.connect(self.uplwin.close)
        worker.progress.connect(self.upload_report_progress)
        thread.finished.connect(lambda: QMessageBox.information(self, 'GUU', lang.popups.upload_complete))
        thread.start()

    def upload_report_progress(self, text):
        self.uplwin.status.setText(text)

    def set_dlselect_lang(self):
        self.dlwin.setWindowTitle("GUU - {}".format(lang.dlselect.remote_path))
        self.dlwin.label.setText(lang.dlselect.remote_pc_info_1)
        self.dlwin.label_2.setText(lang.dlselect.remote_pc_info_2)
        self.dlwin.label_3.setText(lang.dlselect.remote_pc_info_3)

    ###################
    # LOGIN FUNCTIONS #
    ###################

    # Opens login window if user is not logged in,
    # logs out if user is logged in.
    def login(self):
        if api.login_status == 0:
            self.logwin.show()
            self.set_login_lang()
            self.logwin.logwinBtn.clicked.connect(self.sendlogin)
            self.logwin.logwinBtn.setShortcut("Return")
        elif api.login_status == 1:
            api.logout()
            self.checklogin()

    def set_login_lang(self):
        self.logwin.setWindowTitle("GUU - {}".format(lang.login.login))
        self.logwin.label.setText(lang.login.enter_credentials)
        self.logwin.usrLabel.setText(lang.settings.username)
        self.logwin.pwdLabel.setText(lang.settings.password)
        self.logwin.credSave.setText(lang.login.remember_credentials)
        self.logwin.logwinBtn.setText(lang.ui.login)

    # Sends login credentials to the website for authentication
    def sendlogin(self):
        usr = self.logwin.username.text()
        pwd = self.logwin.password.text()

        api.login(usr, pwd)

        api.check_login_status()

        if api.login_status == 1:
            if self.logwin.credSave.isChecked():
                savelgn = int(self.logwin.credSave.isChecked())
                cfg.login_save(savelgn, usr, pwd)
            self.categ_reload()
            self.logwin.close()
            self.checklogin()
        else:
            QMessageBox.warning(self, 'GUU', lang.popups.login_failed)

    ######################
    # PROJECTS FUNCTIONS #
    ######################

    # Clears input widgets and loads the selected project file
    def openproj(self):
        filename = QFileDialog.getOpenFileName(self,
                                               lang.file_dialogs.open_project,
                                               '',
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
        self.picTable.add_pictures(data["Pictures"]["Path(s)"])
        log.new(1, 1, "Loaded project OK.")

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

        saveas = QFileDialog.getSaveFileName(self, lang.file_dialogs.save_file,
                                             'Untitled.guu',
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
            log.new(1, 1, "Saved project OK.")


def show_crash_widget(tb):
    if "SystemExit" not in str(sys.exc_info()[0]):
        win.close_all()
        win.crashwin.show()
        log.new(1, 1, "Showing crash report 2")
        win.crashwin.output.insertPlainText(tb)


def exception_hook(exctype, value, tb):
    sys._excepthook(exctype, value, tb)
    tblist = traceback.format_exception(exctype, value, tb)
    tb = log.get() + "\n"
    for t in tblist:
        tb += t
    tb += "\n"
    show_crash_widget(tb)


if __name__ == '__main__':
    try:
        if getattr(sys, 'frozen', False):
            GUUPATH = sys._MEIPASS
        else:
            GUUPATH = os.path.dirname(os.path.abspath(__file__))
        log = GUULogging()
        cfg = Settings(log)
        api = GayTorrent(log)
        misc = Misc(log)
        languages, languages_full = misc.fetch_lang_packs(
            os.path.join(cfg.data_path, "languages"))
        if languages == []:
            from constants import languages, languages_full
            lang = Language(cfg.language,
                            os.path.join(GUUPATH, "languages"))
        else:
            lang = Language(cfg.language,
                            os.path.join(cfg.data_path, "languages"))
        client = misc.select_client(cfg)
    except:
        appc = QApplication(sys.argv)
        log.new(1, 1, "Showing crash report 1")
        crs = CrashReport(GUUPATH, traceback.format_exc())
        crs.show()
        appc.exec()
    else:
        try:
            app = QApplication(sys.argv)
            if cfg.theme == "system":
                app.setStyleSheet("")
            elif cfg.theme == "dark":
                app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            elif cfg.theme == "light":
                app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            win = Main()
            win.show()
            sys._excepthook = sys.excepthook
            sys.excepthook = exception_hook
            app.exec()
        except:
            text = log.get() + "\n" + traceback.format_exc
            show_crash_widget(text)
