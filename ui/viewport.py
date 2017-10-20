from PyQt5 import QtWidgets, uic


class Viewport(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Viewport, self).__init__(parent)
        uic.loadUi("viewport.ui", self)
        self.show()