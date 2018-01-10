import sys

from PyQt5 import QtWidgets

from ui.lobby import Lobby

import sys
import logging

# Exception handler code:
# https://stackoverflow.com/a/37837374/2958458
# If we don't do this, the exception is left around in the stack
# and becomes an OS-level segfault, which is very difficult to debug.

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    # print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


def main():
    # Start logger
    logging.basicConfig(format='[%(name)s][%(thread)d] %(module)s @%(lineno)d : %(message)s')
    default_logger = logging.getLogger('ac')
    default_logger.setLevel(logging.DEBUG)
    default_logger.info("Logger started")

    app = QtWidgets.QApplication(sys.argv)
    #main_window = MainWindow()
    lobby = Lobby()
    sys.exit(app.exec_())  # exec is a Python keyword, so exec_ is used


if __name__ == '__main__':
    main()