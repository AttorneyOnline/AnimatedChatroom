from PyQt5 import QtCore, QtWidgets, uic

from network.client.client import Client, ClientHandler
from ui.main import MainWindow

import asyncio
from concurrent.futures import ThreadPoolExecutor

import hashlib
from network import packets


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
        client = Client(hostname, port=port)
        loading = Loading(client, self)
        client_thread = ClientThread(client)
        client_thread.on_exception.connect(loading.on_exception)
        client_thread.open_ask_password_dialog.connect(loading.open_ask_password_dialog)
        client_thread.success.connect(loading.success)
        client.handler = Loading.LoadingHandler(client, client_thread)
        client_thread.start()
        loading.exec_()


class ClientThread(QtCore.QThread):

    on_exception = QtCore.pyqtSignal(Exception)
    open_ask_password_dialog = QtCore.pyqtSignal()
    success = QtCore.pyqtSignal()

    def __init__(self, client):
        self._client = client
        super().__init__()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self._client.connect()
        except Exception as e:
            self.on_exception.emit(e)


class Loading(QtWidgets.QDialog, ClientHandler):
    def __init__(self, client: Client, parent=None):
        QtWidgets.QDialog.__init__(self, parent, client=None)
        self.client = client
        self._status = None
        self._progress = None
        uic.loadUi("ui/loading.ui", self)
        self.widget_subdownload.hide()
        self.adjustSize()
        self.show()

    class LoadingHandler(ClientHandler):

        def __init__(self, client: Client, thread: QtCore.QThread):
            super().__init__(client)
            self._thread = thread

        def handle_server_info_response(self, packet: dict):
            self.challenge = packet['auth_challenge']
            if packet['protection'] == packets.ServerInfoResponse.Protection.JOIN_WITH_PASSWORD:
                self._thread.open_ask_password_dialog()
                # TODO: get this thread to wait on UI response
            sha256 = hashlib.sha256()
            sha256.update("abcd".encode("utf-8"))
            sha256.update(self.challenge)
            self.respond(packets.JoinRequest("longboi", sha256.digest()))

    def success(self):
        self.main = MainWindow(self.client, self)
        self.hide()
        self.main.show()

    def on_exception(self, exc: Exception):
        print(exc)
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Connection Error", "Failed to connect to server.", QtWidgets.QMessageBox.Ok)
        self.close()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val: str):
        self.label_status: QtWidgets.QLabel
        self.label_status.setText(val)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val: int):
        self.progress_loading.setValue(val)

    def cancel(self):
        self.close()