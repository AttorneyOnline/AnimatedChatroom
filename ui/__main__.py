import sys
from PyQt5 import QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow): 
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        self.show()

    def open_about(self):
        QtWidgets.QMessageBox.about(self, "Animated Chatroom", "Hi")

    def open_feedback(self):
        pass

    def open_guide(self):
        pass

    def open_howto(self):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())  # exec is a Python keyword, so exec_ is used


if __name__ == '__main__':
    main()