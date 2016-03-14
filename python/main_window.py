__author__ = 'DmitryRa'

from PySide.QtGui import (QMainWindow, QAction, QFileDialog, QApplication, QSplitter)

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.splitter = QSplitter()

        self.setCentralWidget(self.splitter)
        #self.createMenus()
        self.setWindowTitle("Address Book")


if __name__ == "__main__":
    """ Run the application. """
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
