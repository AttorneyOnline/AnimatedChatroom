from PyQt5 import QtWidgets, uic
from ui.spoiler import Spoiler


class SoundMixer(QtWidgets.QDockWidget):
    def __init__(self, parent):
        super(SoundMixer, self).__init__(parent)
        uic.loadUi("sound_mixer.ui", self)

        # Not important to implement right now
        # spoiler = Spoiler(parent=self, title="YES")
        # spoiler.set_content_layout(self.verticalLayout_2)
        # self.horizontalLayout.addWidget(spoiler)

        self.show()

