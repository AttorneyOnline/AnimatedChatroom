from PyQt5 import QtWidgets, uic


class OOCChat(QtWidgets.QDockWidget):
    def __init__(self, parent):
        super(OOCChat, self).__init__(parent)
        uic.loadUi("ui/ooc.ui", self)
        self.show()

