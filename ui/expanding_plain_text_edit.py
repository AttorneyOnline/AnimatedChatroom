from PyQt5 import QtWidgets, QtGui, QtCore


class ExpandingPlainTextEdit(QtWidgets.QTextEdit):

    returnPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document().contentsChanged.connect(self.change_size)

    def change_size(self):
        document_height = self.document().size().height() + 4
        if self.parent() is not None:
            # Target height should be either the text height or the parent height,
            # whichever is smaller
            target_height = min(document_height, self.parent().height())
            # Target height should not be smaller than the absolute minimum height
            target_height = max(target_height, 24)
        else:
            target_height = document_height
        # Force text box size
        self.setMinimumHeight(target_height)
        self.setMaximumHeight(target_height)

    def keyPressEvent(self, keyEvent: QtGui.QKeyEvent):
        if keyEvent.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.returnPressed.emit()
        else:
            QtWidgets.QTextEdit.keyPressEvent(self, keyEvent)