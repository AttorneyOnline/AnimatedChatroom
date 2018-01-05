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
            self.list_rooms.addItem(item)
            self.list_rooms.setItemWidget(item, lbl)

    def done(self, result):
        if result == QtWidgets.QDialog.Accepted:
            rooms_selected = self.list_rooms.selectedItems()
            if len(rooms_selected) != 1:
                self.error("Please select one room to join.")
            else:
                room = rooms_selected[0]
                input_dialog = QtWidgets.QInputDialog()
                response = input_dialog.getText(self, "Password", "Enter the password for the room:")
                if response[1]:
                    try:
                        loop = asyncio.get_event_loop()
                        join_task = loop.create_task(self._client.join_room(rooms_selected[0].id, response[0]))
                        loop.run_until_complete(join_task)
                        result_type = JoinRoomResponse.JoinRoomResult
                        if join_task['result'] == result_type.SUCCESS:
                            self.done(result)
                        elif join_task['result'] == result_type.ROOM_FULL:
                            self.error("This room is full.")
                        elif join_task['result'] == result_type.BAD_PASSWORD:
                            self.error("The password is incorrect.")
                    except ConnectionError:
                        msgbox = QtWidgets.QMessageBox()
                        msgbox.warning(self, "Room Error", "A network error occurred.", QtWidgets.QMessageBox.Ok)
                        self.done(QtWidgets.QDialog.Rejected)

    def error(self, msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.warning(self, "Room Error", msg, QtWidgets.QMessageBox.Ok)