import sys

from PyQt5 import QtWidgets

from ui.main import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())  # exec is a Python keyword, so exec_ is used


if __name__ == '__main__':
    main()