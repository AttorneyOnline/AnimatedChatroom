import asyncio
from PyQt5 import QtCore, QtWidgets, uic
from network.client.client import Client


class Rooms(QtWidgets.QDialog):
    def __init__(self, client: Client, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/rooms.ui", self)
        self._client = client
        loop = asyncio.get_event_loop()
        rooms = loop.create_task(self.get_rooms())
        loop.run_until_complete(rooms)
        self.list_rooms.setModel(RoomListModel(rooms))
        self.show()

    async def get_rooms(self):
        result = await asyncio.wait_for(self._client.get_rooms(), 3)
        return result['rooms']

class RoomListModel(QtCore.QAbstractListModel):
    def __init__(self, rooms: list, parent=None):
        super().__init__(parent)
        self._data = rooms

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return len(self._data)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() <= self.rowCount():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]['name']
        return QtCore.QVariant()