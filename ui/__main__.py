import sys
from PyQt5 import QtWidgets, uic

class MainWindow(QtWidgets.QMainWindow): 
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_()) # exec is a Python keyword, so exec_ is used

if __name__ == '__main__':
    main()