import json
import os


class Language():
    def __init__(self, lang, folder):
        path = os.path.join(folder, "{}.json".format(lang))
        f = json.load(open(path, 'r'))
        self.ui = UI(f)
        self.about = About(f)
        self.login = Login(f)
        self.settings = Settings(f)
        self.dlselect = DLSelect(f)
        self.popups = Popups(f)
        self.file_dialogs = FileDialogs(f)


class UI():
    def __init__(self, f):
        self.file = f["ui"]["file"]
        self.new = f["ui"]["new"]
        self.save = f["ui"]["save"]
        self.open = f["ui"]["open"]
        self.exit = f["ui"]["exit"]
        self.tools = f["ui"]["tools"]
        self.open_webui = f["ui"]["open_webui"]
        self.reload_categories = f["ui"]["reload_categories"]
        self.preferences = f["ui"]["preferences"]
        self.help = f["ui"]["help"]
        self.about = f["ui"]["about"]
        self.path = f["ui"]["path"]
        self.select_folder = f["ui"]["select_folder"]
        self.select_file = f["ui"]["select_file"]
        self.categories = f["ui"]["categories"]
        self.category = f["ui"]["category"]
        self.subcategory1 = f["ui"]["subcategory1"]
        self.subcategory2 = f["ui"]["subcategory2"]
        self.subcategory3 = f["ui"]["subcategory3"]
        self.subcategory4 = f["ui"]["subcategory4"]
        self.select_category = f["ui"]["select_category"]
        self.optional = f["ui"]["optional"]
        self.categories_login_error = f["ui"]["categories_login_error"]
        self.pictures = f["ui"]["pictures"]
        self.add_pictures = f["ui"]["add_pictures"]
        self.remove_pictures = f["ui"]["remove_pictures"]
        self.info = f["ui"]["info"]
        self.title = f["ui"]["title"]
        self.description = f["ui"]["description"]
        self.waiting = f["ui"]["waiting"]
        self.upload = f["ui"]["upload"]
        self.status = f["ui"]["status"]
        self.torrent_client = f["ui"]["torrent_client"]
        self.user = f["ui"]["user"]
        self.unreachable = f["ui"]["unreachable"]
        self.online = f["ui"]["online"]
        self.connected = f["ui"]["connected"]
        self.invalid_credentials = f["ui"]["invalid_credentials"]
        self.none = f["ui"]["none"]
        self.login = f["ui"]["login"]
        self.logout = f["ui"]["logout"]
        self.not_logged_in = f["ui"]["not_logged_in"]


class About():
    def __init__(self, f):
        self.about = f["about"]["about"]
        self.guu = f["about"]["guu"]
        self.made_by = f["about"]["made_by"]
        self.license = f["about"]["license"]
        self.view_license = f["about"]["view_license"]
        self.libraries_used = f["about"]["libraries_used"]


class Login():
    def __init__(self, f):
        self.login = f["login"]["login"]
        self.enter_credentials = f["login"]["enter_credentials"]
        self.remember_credentials = f["login"]["remember_credentials"]


class Settings():
    def __init__(self, f):
        self.settings = f["settings"]["settings"]
        self.general = f["settings"]["general"]
        self.language = f["settings"]["language"]
        self.theme = f["settings"]["theme"]
        self.auto_login = f["settings"]["auto_login"]
        self.username = f["settings"]["username"]
        self.password = f["settings"]["password"]
        self.credentials_warning = f["settings"]["credentials_warning"]
        self.client = f["settings"]["client"]
        self.auto_seed = f["settings"]["auto_seed"]
        self.torrent_client = f["settings"]["torrent_client"]
        self.webui_host = f["settings"]["webui_host"]
        self.webui_port = f["settings"]["webui_port"]
        self.webui_username = f["settings"]["webui_username"]
        self.webui_password = f["settings"]["webui_password"]
        self.uploading = f["settings"]["uploading"]
        self.save_torrents = f["settings"]["save_torrents"]
        self.browse = f["settings"]["browse"]
        self.save = f["settings"]["save"]


class DLSelect():
    def __init__(self, f):
        self.remote_path = f["dlselect"]["remote_path"]
        self.remote_pc_info_1 = f["dlselect"]["remote_pc_info_1"]
        self.remote_pc_info_2 = f["dlselect"]["remote_pc_info_2"]
        self.remote_pc_info_3 = f["dlselect"]["remote_pc_info_3"]


class Popups():
    def __init__(self, f):
        self.new_version = f["popups"]["new_version"]
        self.new_project = f["popups"]["new_project"]
        self.new_project_confirm = f["popups"]["new_project_confirm"]
        self.categories_fetch_login_error = f["popups"]["categories_fetch_login_error"]
        self.client_not_running = f["popups"]["client_not_running"]
        self.client_wrong_credentials = f["popups"]["client_wrong_credentials"]
        self.upload_confirm = f["popups"]["upload_confirm"]
        self.upload_login_error = f["popups"]["upload_login_error"]
        self.torrent_dl_already_exists = f["popups"]["torrent_dl_already_exists"]
        self.torrent_dl_no_permission = f["popups"]["torrent_dl_no_permission"]
        self.upload_complete = f["popups"]["upload_complete"]
        self.login_failed = f["popups"]["login_failed"]
        self.was_not_found = f["popups"]["was_not_found"]


class FileDialogs():
    def __init__(self, f):
        self.select_images = f["file_dialogs"]["select_images"]
        self.open_project = f["file_dialogs"]["open_project"]
        self.save_file = f["file_dialogs"]["save_file"]
