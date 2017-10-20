from PyQt5 import QtCore, QtWidgets


class Spoiler(QtWidgets.QWidget):
    def __init__(self, parent=None, title="Spoiler", animation_duration=300):
        """
        References:
            Adapted from PyQt4 version:
            https://stackoverflow.com/a/37927256 ("Erotemic")
            ...which was in turn adapted from the C++ version:
            https://stackoverflow.com/a/37119983 ("x squared")
        """
        super(Spoiler, self).__init__(parent=parent)

        self.animation_duration = animation_duration
        self.toggleAnimation = QtCore.QParallelAnimationGroup()
        self.contentArea = QtWidgets.QScrollArea()
        self.headerLine = QtWidgets.QFrame()
        self.toggleButton = QtWidgets.QToolButton()
        self.mainLayout = QtWidgets.QGridLayout()

        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(QtCore.Qt.RightArrow)
        self.toggleButton.setText(str(title))
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.headerLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.headerLine.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.contentArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self.contentArea, b"maximumHeight"))

        # don't waste space
        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        self.mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        self.toggleButton.clicked.connect(self.start_animation)

    def start_animation(self, checked):
        if checked:
            arrow_type = QtCore.Qt.DownArrow
            direction = QtCore.QAbstractAnimation.Forward
        else:
            arrow_type = QtCore.Qt.RightArrow
            direction = QtCore.QAbstractAnimation.Backward
        self.toggleButton.setArrowType(arrow_type)
        self.toggleAnimation.setDirection(direction)
        self.toggleAnimation.start()

    def set_content_layout(self, content_layout):
        self.contentArea.destroy()
        self.contentArea.setLayout(content_layout)

        collapsed_height = self.sizeHint().height() - self.contentArea.maximumHeight()
        content_height = content_layout.sizeHint().height()

        for i in range(self.toggleAnimation.animationCount() - 1):
            spoiler_animation = self.toggleAnimation.animationAt(i)
            spoiler_animation.setDuration(self.animation_duration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        content_animation.setDuration(self.animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)