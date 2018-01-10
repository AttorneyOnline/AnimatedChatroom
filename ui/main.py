from PyQt5 import QtCore, QtWidgets, uic

from . import show_exception_dialog
from .rooms import Rooms
from .viewport import Viewport
from .sound_mixer import SoundMixer
from .ooc import OOCChat
from .ic import ICChat
from network.client.client import Client


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, client: Client, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/main.ui", self)

        self.client = client
        self.client.thread.on_disconnect.connect(self.on_disconnect)
        self.client.thread.on_exception.connect(self.on_exception)
        self.viewport = Viewport(self)

        # Windows/dock widgets: a mapping from widget type to the actual
        # object
        self.windows = dict()

        self.load_widgets()
        self.setWindowTitle("{} - Animated Chatroom".format(self.client.server_info['name']))
        self.show()
        try:
            rooms = Rooms(client, parent=self)
            rooms.setWindowModality(QtCore.Qt.WindowModal)
            result = rooms.exec_()
            if result != QtWidgets.QDialog.Accepted:
                self.close()
        except Exception as e:
            msgbox = QtWidgets.QMessageBox()
            msgbox.critical(self, "Rooms Error", "There was an error retrieving the room list.",
                            QtWidgets.QMessageBox.Ok)
            self.close()

    def on_disconnect(self):
        msgbox = QtWidgets.QMessageBox(self)
        msgbox.setWindowTitle("Disconnected")
        msgbox.setText("You have been disconnected from the server.")
        msgbox.setWindowModality(QtCore.Qt.WindowModal)
        msgbox.setIcon(QtWidgets.QMessageBox.Warning)
        msgbox.exec_()

    def on_exception(self, exc: Exception):
        show_exception_dialog(self, exc)

    def load_widgets(self):
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.viewport)
        self.setCentralWidget(self.viewport)
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, SoundMixer(self))
        self.add_dock_widget(OOCChat(self), QtCore.Qt.RightDockWidgetArea)
        self.add_dock_widget(ICChat(self), QtCore.Qt.RightDockWidgetArea)

    def add_dock_widget(self, widget: QtWidgets.QDockWidget, target: int):
        self.addDockWidget(target, widget)
        self.windows[type(widget)] = widget
        widget.destroyed.connect(lambda: self.remove_dock_widget(widget))

    def remove_dock_widget(self, widget: QtWidgets.QDockWidget):
        del self.windows[type(widget)]

    def closeEvent(self, event):
        self.client.close()

    def open_about(self):
        QtWidgets.QMessageBox.about(self, "Animated Chatroom", "Hi")

    def open_feedback(self):
        pass

    def open_guide(self):
        pass

    def open_howto(self):
        pass