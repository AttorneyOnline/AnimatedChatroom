from PyQt5 import QtCore, QtWidgets, uic
from ui.viewport import Viewport
from ui.sound_mixer import SoundMixer
from ui.ooc import OOCChat
from network.client.client import Client


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, client: Client, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/main.ui", self)

        self._client = client
        self.viewport = Viewport(self)

        self.load_widgets()
        self.show()

    def load_widgets(self):
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.viewport)
        self.setCentralWidget(self.viewport)
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, SoundMixer(self))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, OOCChat(self))

    def closeEvent(self, event):
        self._client.close()

    def open_about(self):
        QtWidgets.QMessageBox.about(self, "Animated Chatroom", "Hi")

    def open_feedback(self):
        pass

    def open_guide(self):
        pass

    def open_howto(self):
        pass