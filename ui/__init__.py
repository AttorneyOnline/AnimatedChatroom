import traceback

from PyQt5 import QtWidgets, QtGui, QtCore


def show_exception_dialog(parent: QtWidgets.QWidget, exc: Exception):
    """
    Displays a standard error message box with a preformatted text box
    describing the exception."""
    msgbox = QtWidgets.QMessageBox(parent)
    msgbox.setDetailedText(f'{"".join(traceback.format_tb(exc.__traceback__))}\n{str(exc)}')
    mono_font_name = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont).family()
    msgbox.setStyleSheet(
        f'QTextEdit {{ background-color: #272822;'
        f'color: #fff;'
        f'font-family: {mono_font_name};'
        f'min-width: 600px; }}')
    msgbox.setWindowTitle("Connection Error")
    msgbox.setText("Failed to connect to server.")
    msgbox.setWindowModality(QtCore.Qt.WindowModal)
    msgbox.setIcon(QtWidgets.QMessageBox.Critical)
    msgbox.adjustSize()
    msgbox.exec_()
