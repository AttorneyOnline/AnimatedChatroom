import asyncio
import random
import threading
import logging

from PyQt5 import QtCore, QtWidgets, uic, QtGui

from network import packets
from network.client.client import Client, ClientHandler
from . import show_exception_dialog
from .main import MainWindow

ui_logger = logging.getLogger("ac.ui.lobby")


class Lobby(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.master_server = None
        self.client_threads = set()
        self.windows = []
        uic.loadUi("ui/lobby.ui", self)
        self.show()

    def closeEvent(self, event):
        for client_thread in self.client_threads:
            client_thread.stop()

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
        client = Client(hostname, port=port, master=True)
        loading = Loading(client, self)
        loading.open_main.connect(self._connect_success)

        thread_id_future = asyncio.Future()
        client_thread = ClientThread(client, parent=loading, thread_id_future=thread_id_future)
        client_thread.open_password_dialog.connect(loading.ask_password, QtCore.Qt.BlockingQueuedConnection)
        client_thread.on_exception.connect(loading.on_exception, QtCore.Qt.BlockingQueuedConnection)
        client_thread.on_disconnect.connect(loading.on_disconnect)
        client_thread.success.connect(loading.success)
        client_thread.error.connect(loading.error, QtCore.Qt.BlockingQueuedConnection)
        client_thread.set_status.connect(loading.set_status)
        client_thread.set_progress.connect(loading.set_progress)
        client_thread.thread_end.connect(self._thread_stopped)

        client.handler = Loading.LoadingHandler(client, client_thread)
        client_thread.start()
        thread_id_future.add_done_callback(lambda: self.client_threads.add(client_thread))
        loading.show()

    def _connect_success(self, client):
        self.windows.append(MainWindow(client, None))
        # self.main.show()
        # Code below causes application to close.
        # self.hide()

    def _thread_stopped(self, thread: QtCore.QThread):
        self.client_threads.discard(thread)
        ui_logger.debug("Discarded thread %d from thread list.", thread.thread_id)


class ClientThread(QtCore.QThread):

    client_logger = logging.getLogger("ac.t.client")

    on_exception = QtCore.pyqtSignal(Exception)
    on_disconnect = QtCore.pyqtSignal()
    success = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    thread_end = QtCore.pyqtSignal(QtCore.QThread)

    set_status = QtCore.pyqtSignal(str)
    set_progress = QtCore.pyqtSignal(int)
    show_subprogress = QtCore.pyqtSignal(bool)
    set_substatus = QtCore.pyqtSignal(str)
    set_subprogress = QtCore.pyqtSignal(int)

    open_password_dialog = QtCore.pyqtSignal(asyncio.Future)

    def __init__(self, client, parent=None, thread_id_future: asyncio.Future = None):
        super().__init__()
        self._client = client
        self._client.thread = self
        self._parent = parent
        self._thread_id_future = thread_id_future

        # To be populated after the thread starts.
        self.thread_id = None

    def __hash__(self):
        """Get the identifier of the client thread."""
        return self.thread_id

    def __eq__(self, other):
        """Naive equals."""
        return self.__hash__() == other.__hash__()

    def __del__(self):
        self.client_logger.debug("Thread {} freed", self.thread_id)

    def run(self):
        self.thread_id = threading.get_ident()
        self.client_logger.info("Master client thread %d spawned", self.thread_id)
        if self._thread_id_future is not None:
            self._thread_id_future.set_result(self.thread_id)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._disconnect_future = self.loop.create_future()
        self.loop.run_until_complete(self._connect())
        try:
            self.loop.run_until_complete(self._disconnect_future)
        except asyncio.CancelledError:
            pass
        self.thread_end.emit(self)
        self.client_logger.info("Client thread closed.")

    async def _connect(self):
        self.set_status.emit("Connecting to server...")
        self.set_progress.emit(0)
        try:
            await self._client.connect(self._disconnect_future)
        #except TimeoutError:
        #    self.error.emit("The connection to the server timed out.")
        #    return
        except OSError as e:
            self.on_exception.emit(e)
            return

        self.set_status.emit("Getting server info...")
        self.set_progress.emit(20)
        server_info = await self._client.get_server_info()
        self._client.server_info = server_info
        password = None
        try:
            if server_info['protection'] == packets.ServerInfoResponse.Protection.JOIN_WITH_PASSWORD:
                # Blocking queued connection - will block until dialog is closed
                password = await self._ask_password()
                print(password)
            await self._client.join_server("longboi", password)
        except InterruptedError:
            self._client.close()
            self.on_disconnect.emit()
            return
        except ConnectionError as e:
            self._client.close()
            self.error.emit(str(e))
            return
        except Exception as e:
            self._client.close()
            self.on_exception.emit(e)
            return

        # TODO: download assets

        self.set_status.emit("Loading client...")
        self.set_progress.emit(90)
        self.success.emit()

    async def _ask_password(self):
        future = asyncio.Future()
        self.open_password_dialog.emit(future)
        return await future

    def stop(self):
        self._client.close()
        self.loop.call_soon_threadsafe(self.loop.stop)


class Loading(QtWidgets.QDialog):

    open_main = QtCore.pyqtSignal(Client)

    def __init__(self, client: Client, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
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

        def handle_disconnect(self):
            super().handle_disconnect()
            self._thread.on_disconnect.emit()

    def error(self, msg: str):
        msgbox = QtWidgets.QMessageBox()
        msgbox.critical(self, "Connection Error", msg, QtWidgets.QMessageBox.Ok)
        self.close()
        self.deleteLater()

    def on_exception(self, exc: Exception):
        show_exception_dialog(self, exc)
        self.on_disconnect()

    def on_disconnect(self):
        # This assumes that the disconnect was either graceful or there was an exception
        # already handled.
        self.close()
        self.deleteLater()

    def ask_password(self, future: asyncio.Future):
        input_dialog = QtWidgets.QInputDialog()
        response = input_dialog.getText(self, "Password", "This server requires a password to join.")
        if not response[1]:
            future.set_exception(InterruptedError())
        else:
            future.set_result(response[0])

    def success(self):
        self.widget_subdownload.hide()
        self.open_main.emit(self.client)
        self.close()
        self.deleteLater()

    @property
    def status(self):
        return self._status

    def set_status(self, val: str):
        self.label_status: QtWidgets.QLabel
        self.label_status.setText(val)

    @property
    def progress(self):
        return self._progress

    def set_progress(self, val: int):
        self.progress_loading.setValue(val)

    def cancel(self):
        ui_logger.info("Canceling loading process!")
        self.client.close()
        self.close()
