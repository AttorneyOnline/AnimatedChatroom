import asyncio
from . import icons
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from network.client.client import Client
from network.packets import ServerInfoResponse, JoinRoomResponse


class Rooms(QtWidgets.QDialog):
    def __init__(self, client: Client, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/rooms.ui", self)
        self._client = client
        for room in self._client.server_info['rooms']:
            item = QtWidgets.QListWidgetItem(self.list_rooms)
            lbl = QtWidgets.QLabel()
            protection = ServerInfoResponse.Protection
            icon = None
            if room['protection'] == protection.JOIN_WITH_PASSWORD:
                icon = icons.LOCKED
            elif room['protection'] == protection.WHITELIST:
                icon = icons.WHITELIST
            elif room['protection'] == protection.CLOSED:
                icon = icons.NO_ENTRY
            img_tag = '<img align="right" src="{}"/>'.format(icon) if icon else ""
            lbl.setText('<h1>{}</h1>{}<p>{}</p>'.format(room['name'], img_tag, room['description']))
            item.setSizeHint(lbl.sizeHint() + QtCore.QSize(0, 25))
            item.id = room['id']
            item.password = room['protection']
            self.list_rooms.addItem(item)
            self.list_rooms.setItemWidget(item, lbl)

    def accept(self):
        rooms_selected = self.list_rooms.selectedItems()
        if len(rooms_selected) != 1:
            self.error("Please select one room to join.")
        else:
            room = rooms_selected[0]
            try:
                if room.password:
                    self.get_password(room)
                join_task = self.join_room(room)
                result_type = JoinRoomResponse.JoinRoomResult
                if join_task['result_code'] == result_type.SUCCESS:
                    self.done(QtWidgets.QDialog.Accepted)
                elif join_task['result_code'] == result_type.BAD_PASSWORD:
                    self.error("The password is incorrect.")
                elif join_task['result_code'] == result_type.ROOM_FULL:
                    self.error("This room is full.")
            except InterruptedError:
                # Get password dialog was closed. Go back to the dialog.
                pass
            except (ConnectionError, asyncio.TimeoutError):
                msgbox = QtWidgets.QMessageBox()
                msgbox.error(self, "Room Error", "A network error occurred.", QtWidgets.QMessageBox.Ok)
                self.done(QtWidgets.QDialog.Rejected)

    def join_room(self, room, password=None):
        # If we try to do a standard async call, then we will run it on the wrong loop (UI thread)!
        # We need to ensure we call the coroutine on the client thread's loop, because otherwise
        # the future never gets fulfilled (messages are being handled on the client thread)
        # and the UI thread stalls.
        future = asyncio.run_coroutine_threadsafe(self._client.join_room(room.id, password), self._client.loop)
        return future.result(3)

    def get_password(self, room: QtWidgets.QListWidgetItem):
        input_dialog = QtWidgets.QInputDialog()
        response = input_dialog.getText(self, "Password", "Enter the password for the room:")
        if response[1]:
            return response[0]
        raise InterruptedError

    def error(self, msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.warning(self, "Room Error", msg, QtWidgets.QMessageBox.Ok)