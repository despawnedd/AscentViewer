from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import ctypes
import json
import logging
import os
import platform
import glob
import datetime
import signal

ver = "Early Test ver 2"
date_format_file = "%d%m%Y_%H%M%S"
date_format = "%d/%m/%Y %H:%M:%S"

logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.txt"
ascv_logger = logging.getLogger("AscV Logger")
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), logging.FileHandler(logfile)], format="[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s", datefmt=date_format)
if os.path.exists(logfile):
    with open(logfile, "w") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
        m = "="*15 + "[ BEGIN LOG ]" + "="*15
        f.write(f"{m}\n")
        print(m)

ascv_logger.info(f"The OS is {platform.system()}.")

if platform.system() == "Windows":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ascv")

signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work in console

class MainClass(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # non-gui related stuff
        ascv_logger.info("Initializing GUI.")
        self.dirPath = ""

        # gui related stuff
        self.resize(800, 600)
        self.setWindowTitle(f"AscentViewer {ver}")
        self.setWindowIcon(QtGui.QIcon("data/assets/icon22.png"))

        self.imgFilePath = ""
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

        self.navButtonBack = QtWidgets.QAction(QtGui.QIcon(), "Previous Image", self)
        self.navButtonBack.setShortcut("Left")
        self.navButtonBack.setStatusTip("Go to previous image in directory")
        self.navButtonBack.triggered.connect(self.prevImage)

        self.navButtonForw = QtWidgets.QAction(QtGui.QIcon(), "Next Image", self)
        self.navButtonForw.setShortcut("Right")
        self.navButtonForw.setStatusTip("Go to next image in directory")
        self.navButtonForw.triggered.connect(self.nextImage)

        logWindowButton = QtWidgets.QAction(QtGui.QIcon(), "Log Viewer", self)
        logWindowButton.setShortcut("CTRL+Shift+L")
        logWindowButton.setStatusTip("Open the log viewer window.")
        logWindowButton.triggered.connect(self.openLogViewerWin)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        self.navButtonBack.setEnabled(False)
        navMenu.addAction(self.navButtonBack)
        self.navButtonForw.setEnabled(False)
        navMenu.addAction(self.navButtonForw)

        debugMenu.addAction(logWindowButton)

        ascv_logger.info("GUI has been initialized.")
    
    # i should clean up these two functions below soon
    def openImage(self):
        self.imgFilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image File", "C:\\", "Image files (*.jpg *.jpeg *.gif *.png *.bmp)")
        if self.imgFilePath != "":
            ascv_logger.info(f"Opened image. Image path: \"{self.imgFilePath}\"")
            self.dirPath_ = self.imgFilePath.replace(os.path.basename(self.imgFilePath), "")
            ascv_logger.info(f"Image's directory path: \"{self.dirPath_}\"")

            ascv_logger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascv_logger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    ascv_logger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(1)
                else:
                    ascv_logger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
            else:
                ascv_logger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)

            self.updateImage()

            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascv_logger.info("imgFilePath is empty!")

    def openDir(self):
        self.dirPath_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Open a Directory", "C:\\")
        if self.dirPath_ != "":
            ascv_logger.info(f"Successfully opened directory, directory path is: \"{self.dirPath_}\"")

            ascv_logger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascv_logger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    ascv_logger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(0)
                else:
                    ascv_logger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
            else:
                ascv_logger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(0)

            self.updateImage()
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascv_logger.info("dirPath_ is blank!")

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList = []

        for files in fileTypes:
            self.dirImageList.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList = [files.replace('\\', '/') for files in self.dirImageList]
        self.dirImageList.sort(key=str.lower)
        
        ascv_logger.info(f"Succesfully created dirImageList, dirImageList length: {len(self.dirImageList)}")
        # ascv_logger.debug(f"dirImageList: {self.dirImageList}") # ---> this SOMETIMES pukes out a unicode error, "UnicodeEncodeError: 'charmap' codec can't encode character '\u010d' in position 1125: character maps to <undefined>", no idea why, probably something with the files that you open

        if hasOpenedImage == 1:
            self.imageNumber = self.dirImageList.index(self.imgFilePath)
        else:
            self.imageNumber = 0

        print(self.imageNumber)

        self.imgFilePath = self.dirImageList[self.imageNumber]

    def updateImage(self):
        mwWidth = self.mainWidget.frameGeometry().width()
        mwHeight = self.mainWidget.frameGeometry().height()

        if self.imgFilePath != "":
            self.pixmap1 = QtGui.QPixmap(self.imgFilePath)
            self.pixmap = self.pixmap1.scaled(mwWidth, mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap)
        self.label.resize(mwWidth, mwHeight)

    def resizeEvent(self, event):
        self.updateImage()

    def prevImage(self):
        print("prev image")
        self.imageNumber -= 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        print(self.imageNumber)
        self.updateImage()

    def nextImage(self):
        print("next image")
        self.imageNumber += 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        print(self.imageNumber)
        self.updateImage()

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
                ascv_logger.info("Exiting...")
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
        
        logTextEdit.appendPlainText("Coming soon. In t\n====================")

        #logging.info("Log Viewer works!")
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainClass()
    window.show()
    window.statusBar().showMessage(f"Succesfully loaded. Version: {ver}")

    sys.exit(app.exec_())
