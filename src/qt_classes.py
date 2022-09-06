from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtGui import QIcon


class GUUClasses(object):
    class PictureList(QListWidget):
        def __init__(self, type, parent=None):
            super(GUUClasses.PictureList, self).__init__(parent)
            self.setAcceptDrops(True)

        def dragEnterEvent(self, event):
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()

        def dropEvent(self, event):
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            self.add_pictures(files)

        def add_pictures(self, list):
            for pic in list:
                icon = QIcon(pic)
                item = QListWidgetItem(icon, pic)
                self.addItem(item)
