from PyQt5 import QtWidgets, uic


class ICChat(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/ic.ui", self)
        self.show()

