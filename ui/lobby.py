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
        self.client_threads = []
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
        loading.open_main.connect(self._connect_success)
        client_thread = ClientThread(client)
        client_thread.on_exception.connect(loading.on_exception)
        client_thread.open_ask_password_dialog.connect(loading.open_ask_password_dialog)
        client_thread.success.connect(loading.success)
        client_thread.error.connect(loading.error)
        client.handler = Loading.LoadingHandler(client, client_thread)
        client_thread.start()
        self.client_threads.append(client_thread)
        loading.show()

    def _connect_success(self, client):
        self.main = MainWindow(client, self)
        self.main.show()
        # Code below causes application to close.
        # self.hide()

class ClientThread(QtCore.QThread):

    on_exception = QtCore.pyqtSignal(Exception)
    open_ask_password_dialog = QtCore.pyqtSignal()
    success = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self, client):
        self._client = client
        super().__init__()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        connect_task = asyncio.Task(self._client._connect())
        connect_task.add_done_callback(self.connect_done)
        self.loop.run_forever()
        print("Client thread closed.")

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def connect_done(self, future: asyncio.Future):
        if future.exception():
            self.on_exception.emit(future.exception())
            return
        # HACK: on connection loss, kill the event loop
        self._client._transport[1].connection_lost = \
            lambda exc: self.stop()
        self._client.get_server_info()

class Loading(QtWidgets.QDialog, ClientHandler):

    open_main = QtCore.pyqtSignal(Client)

    def __init__(self, client: Client, parent=None):
        QtWidgets.QDialog.__init__(self, parent, client=None)
        self.client = client
        self._status = None
        self._progress = None
        uic.loadUi("ui/loading.ui", self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.widget_subdownload.hide()
        self.adjustSize()
        self.show()

    class LoadingHandler(ClientHandler):

        def __init__(self, client: Client, thread: QtCore.QThread):
            super().__init__(client)
            self._thread = thread

        def handle_connect(self):
            self.client.get_server_info()

        def handle_disconnect(self):
            self._thread.stop()

        def handle_server_info_response(self, packet: dict):
            self.client.challenge = packet['auth_challenge']
            if packet['protection'] == packets.ServerInfoResponse.Protection.JOIN_WITH_PASSWORD:
                self._thread.open_ask_password_dialog.emit()
            else:
                self.client.join_server("longboi")

        def handle_join_response(self, packet: dict):
            if packet['result_code'] == packets.JoinResponse.JoinResult.SUCCESS:
                self._thread.success.emit()
            elif packet['result_code'] == packets.JoinResponse.JoinResult.SERVER_FULL:
                self._thread.error.emit("The server is full.")
            elif packet['result_code'] == packets.JoinResponse.JoinResult.BAD_PASSWORD:
                self._thread.error.emit("The password was incorrect.")
            else:
                print(packet['result_code'])
                self._thread.error.emit("The join result was not understood.")

    def open_ask_password_dialog(self):
        input_dialog = QtWidgets.QInputDialog()
        response = input_dialog.getText(self, "Password", "This server requires a password to join.")
        if not response[1]:
            self.client.close()
            self.close()
            return
        self.client.join_server("longboi", password=response[0])

    def error(self, msg: str):
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Connection Error", msg, QtWidgets.QMessageBox.Ok)
        self.close()

    def on_exception(self, exc: Exception):
        print(exc)
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Connection Error", "Failed to connect to server.", QtWidgets.QMessageBox.Ok)
        self.close()

    def success(self):
        self.open_main.emit(self.client)
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