import asyncio
from PyQt5 import QtGui, QtWidgets, uic, QtCore


class ICChat(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/ic.ui", self)
        self.chat_entry.returnPressed.connect(self.sendMessage)
        self.show()

    def sendMessage(self):
        msg = self.chat_entry.document().toPlainText()
        client = self.parent().client
        asyncio.run_coroutine_threadsafe(client.send_message(room_id=client.current_room_id, text=msg, emote="emote1"),
                                         client.loop)
