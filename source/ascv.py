from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import ctypes
import json
import logging
import os
import glob
import datetime
import signal

ver = "Early Test ver 2"
date_format_file = "%d%m%Y_%H%M%S"
date_format = "%d/%m/%Y %H:%M:%S"

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ascv")
signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work in console

logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.txt"
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), logging.FileHandler(logfile)], format="[%(asctime)s | %(funcName)s | %(levelname)s] %(message)s", datefmt=date_format)
logger = logging.getLogger(__name__)
if os.path.exists(logfile):
    with open(logfile, "w") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
        m = "="*15 + "[ BEGIN LOG ]" + "="*15
        f.write(f"{m}\n")
        print(m)

class MainClass(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # non-gui related stuff
        # ...

        # gui related stuff
        self.resize(800, 600)
        self.setWindowTitle(f"AscentViewer {ver}")
        self.setWindowIcon(QtGui.QIcon("data/assets/icon22.png"))

        self.imgFileName = ""
        self.exitPromptEnabled = True

        self.mainWidget = QtWidgets.QWidget(self)

        self.setCentralWidget(self.mainWidget)

        self.label = QtWidgets.QLabel(self.mainWidget)
        
        self.label.setText("Please open an image file.")

        mainLabelFont = QtGui.QFont()
        mainLabelFont.setBold(True)
        mainLabelFont.setPointSize(32)
        self.label.setFont(mainLabelFont)
        self.label.setMinimumSize(1, 1)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        navMenu = mainMenu.addMenu("Navigation")
        debugMenu = mainMenu.addMenu("Debug")
        helpMenu = mainMenu.addMenu("Help")

        exitButton = QtWidgets.QAction(QtGui.QIcon("data/assets/door.png"), "Exit", self)
        exitButton.setShortcut("Alt+F4")
        exitButton.setStatusTip("Exit application")
        exitButton.triggered.connect(self.close)

        openImgButton = QtWidgets.QAction(QtGui.QIcon("data/assets/file.png"), "Open Image...", self)
        openImgButton.setShortcut("CTRL+O")
        openImgButton.setStatusTip("Open an image file")
        openImgButton.triggered.connect(self.openImage)

        openDirButton = QtWidgets.QAction(QtGui.QIcon("data/assets/file.png"), "Open Directory...", self)
        openDirButton.setShortcut("CTRL+Shift+O")
        openDirButton.setStatusTip("Open a directory file")
        openDirButton.triggered.connect(self.openDir)

        navButtonBack = QtWidgets.QAction(QtGui.QIcon(), "Previous Image", self)
        navButtonBack.setShortcut("Left")
        navButtonBack.setStatusTip("Go to previous image in directory")
        navButtonBack.triggered.connect(self.prevImage)

        navButtonForw = QtWidgets.QAction(QtGui.QIcon(), "Next Image", self)
        navButtonForw.setShortcut("Right")
        navButtonForw.setStatusTip("Go to next image in directory")
        navButtonForw.triggered.connect(self.nextImage)

        logWindowButton = QtWidgets.QAction(QtGui.QIcon(), "Log Viewer", self)
        logWindowButton.setShortcut("CTRL+Shift+L")
        logWindowButton.setStatusTip("Open the log viewer window.")
        logWindowButton.triggered.connect(self.openLogViewerWin)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        navMenu.addAction(navButtonBack)
        navMenu.addAction(navButtonForw)

        debugMenu.addAction(logWindowButton)

    def openImage(self):
        self.imgFileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image File", "C:\\", "Image files (*.jpg *.jpeg *.gif *.png *.bmp)")
        print(_)
        self.pixmap1 = QtGui.QPixmap(self.imgFileName)
        print(self.imgFileName)
        self.resizeEvent(self.event)

    def openDir(self):
        self.dirName = QtWidgets.QFileDialog.getExistingDirectory(self, "Open a Directory", "C:\\")
        self.dirMakeImageList(0)

    def dirMakeImageList(self, hasOpenedImage):
        print(hasOpenedImage)
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList = []

        for files in fileTypes:
            self.dirImageList.extend(glob.glob(f"{self.dirName}/{files}"))

        self.dirImageList = [files.replace('\\', '/') for files in self.dirImageList]
        self.dirImageList.sort(key=str.lower)

        print(f"dirImageList: {self.dirImageList}, dirImageList length: {len(self.dirImageList)}")

        #if hasOpenedImage == 1:
        #    imageNumber = self.dirImageList.index(filePath)
        #else:
        #    imageNumber = 0

        #filePath = dirImageList[imageNumber]

    def resizeEvent(self, event):
        mwWidth = self.mainWidget.frameGeometry().width()
        mwHeight = self.mainWidget.frameGeometry().height()

        if self.imgFileName != "":
            self.pixmap1 = QtGui.QPixmap(self.imgFileName)
            self.pixmap = self.pixmap1.scaled(mwWidth, mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap)
        self.label.resize(mwWidth, mwHeight)

    def prevImage(self):
        print("prev image")

    def nextImage(self):
        print("next image")

    def openLogViewerWin(self):
        self.logViewerWin = LogViewer()
        self.logViewerWin.show()

    def closeEvent(self, event):
        if self.exitPromptEnabled != False:
            reply = QtWidgets.QMessageBox(self)
            reply.setWindowIcon(QtGui.QIcon("data/assets/icon22.png"))
            reply.setWindowTitle("Exiting AscentViewer")
            reply.setText("<b>Are you sure you want to exit AscentViewer?</b>")
            reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            reply.setDefaultButton(QtWidgets.QMessageBox.No)
            checkbox = QtWidgets.QCheckBox("Do not show this again, instead, exit without asking next time.")

            icon1 = QtGui.QPixmap("data/assets/door.png")
            icon = icon1.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            reply.setIconPixmap(QtGui.QPixmap(icon))
            reply.setCheckBox(checkbox)

            reply.setModal(True)
            x = reply.exec_()

            if x == QtWidgets.QMessageBox.Yes:
                print("Exiting...")
                event.accept()
            else:
                print("Not exiting.")
                event.ignore()

            if checkbox.isChecked():
                print("Disabling prompt...")
                self.exitPromptEnabled = False
            else:
                print("Not disabling prompt.")

        else:
            print("This entire prompt is disabled, exiting...")

class LogViewer(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.resize(600, 400)
        self.setWindowTitle("Log Viewer")
        self.setWindowIcon(QtGui.QIcon("data/assets/icon22.png"))

        logTextEdit = QtWidgets.QPlainTextEdit(self)
        logTextEdit.resize(600, 400)
        
        logTextEdit.appendPlainText("LOG STARTS HERE\n====================")

        logging.info("Log Viewer works!")
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainClass()
    window.show()
    window.statusBar().showMessage(f"Succesfully loaded. Version: {ver}")

    sys.exit(app.exec_())
