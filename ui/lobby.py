from PyQt5 import QtCore, QtWidgets, uic

class Lobby(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.master_server = None
        uic.loadUi("ui/lobby.ui", self)
        self.show()

    def master_server_refresh(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Error", "Master server doesn't exist yet, dummy.", QtWidgets.QMessageBox.Help)

    def server_add_to_favorites(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Error", "You can't add things to favorites either, dummy.", QtWidgets.QMessageBox.Help)

    def open_direct_connect_dialog(self):
        input_dialog = QtWidgets.QInputDialog()
        response = input_dialog.getText(self, "Direct Connect", "Enter the hostname and port of the server:",
                                       QtWidgets.QLineEdit.Normal,
                                       "localhost:42505")
        if not response[1]:
            # Cancel
            return
        try:
            hostname, port = response[0].split(':')
            # Connect to client
            self._start_connect(hostname, int(port))
        except ValueError:
            msgbox = QtWidgets.QMessageBox()
            response = msgbox.warning(self, "Bad address", "Incorrect address format.",
                            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Retry)
            if response == QtWidgets.QMessageBox.Retry:
                self.open_direct_connect_dialog()

    def _start_connect(self, hostname, port):
        Loading(self).exec_()

class Loading(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/loading.ui", self)
        self.show()

    def cancel(self):
        self.close()