import sys
import os

from PyQt5.uic          import loadUi
from PyQt5.QtGui        import QPixmap
from PyQt5.QtGui        import QIcon
from PyQt5.QtWidgets    import *

from main_function import main_function

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = loadUi(resource_path('main_v2_0.ui'), self)
        self.ui.hbrain_icon.setPixmap(QPixmap(resource_path("hbrain_logo.png")))
        self.setWindowIcon(QIcon(resource_path("hbrain.png")))
        self.mf = main_function(self.ui)

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # try:
        #     # PyInstaller creates a temp folder and stores path in _MEIPASS
        #     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        #     print("base_path:", base_path)
        # except Exception:
        base_path = os.path.abspath(".")

        # return os.path.join(base_path, './', relative_path)
        return os.path.join(base_path, relative_path)

import binascii
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec_()
