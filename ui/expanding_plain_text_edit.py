from PyQt5 import QtWidgets


class ExpandingPlainTextEdit(QtWidgets.QTextEdit):

    def __init__(self, parent=None):
        super(ExpandingPlainTextEdit, self).__init__(parent)
        self.document().contentsChanged.connect(self.change_size)

    def change_size(self):
        document_height = self.document().size().height() + 4
        if self.parent() is not None:
            target_height = min(document_height, self.parent().height())
        else:
            target_height = document_height
        self.setMinimumHeight(target_height)