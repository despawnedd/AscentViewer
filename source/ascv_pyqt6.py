from PyQt6 import QtGui, QtCore, QtWidgets
import sys
import ctypes
import json
import logging
import os
import platform
import glob
import datetime
import signal

class MainClass(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # non-gui related stuff
        ascvLogger.info("Initializing GUI.")
        self.dirPath = ""
        self.imgFilePath = ""

        # gui related stuff
        self.resize(config["windowProperties"]["width"], config["windowProperties"]["height"])
        self.setWindowTitle(f"AscentViewer {ver}")
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon22.png"))

        self.mainWidget = QtWidgets.QWidget(self)

        self.setCentralWidget(self.mainWidget)

        self.label = QtWidgets.QLabel(self.mainWidget)

        self.label.setText("Please open an image file.")

        mainLabelFont = QtGui.QFont()
        mainLabelFont.setBold(True)
        mainLabelFont.setPointSize(32)
        self.label.setFont(mainLabelFont)

        self.label.setMinimumSize(1, 1)
        self.label.setAlignment(QtCore.Qt.Alignment.AlignCenter)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        navMenu = mainMenu.addMenu("Navigation")
        if config["debug"]["enableDebugMenu"]:
            debugMenu = mainMenu.addMenu("Debug")
        helpMenu = mainMenu.addMenu("Help")
        
        exitButton = QtGui.QAction(QtGui.QIcon("data/assets/img/door.png"), "Exit", self)
        exitButton.setShortcut("Alt+F4")
        exitButton.setStatusTip("Exit application")
        exitButton.triggered.connect(self.close)

        openImgButton = QtGui.QAction(QtGui.QIcon("data/assets/img/file.png"), "Open Image...", self)
        openImgButton.setShortcut("CTRL+O")
        openImgButton.setStatusTip("Open an image file")
        openImgButton.triggered.connect(self.openImage)

        openDirButton = QtGui.QAction(QtGui.QIcon("data/assets/img/file.png"), "Open Directory...", self)
        openDirButton.setShortcut("CTRL+Shift+O")
        openDirButton.setStatusTip("Open a directory file")
        openDirButton.triggered.connect(self.openDir)

        self.navButtonBack = QtGui.QAction(QtGui.QIcon(), "Previous Image", self)
        self.navButtonBack.setShortcut("Left")
        self.navButtonBack.setStatusTip("Go to previous image in directory")
        self.navButtonBack.triggered.connect(self.prevImage)

        self.navButtonForw = QtGui.QAction(QtGui.QIcon(), "Next Image", self)
        self.navButtonForw.setShortcut("Right")
        self.navButtonForw.setStatusTip("Go to next image in directory")
        self.navButtonForw.triggered.connect(self.nextImage)

        if config["debug"]["enableDebugMenu"]:
            logWindowButton = QtWidgets.QAction(QtGui.QIcon(), "Log Viewer", self)
            logWindowButton.setShortcut("CTRL+Shift+L")
            logWindowButton.setStatusTip("Open the log viewer window.")
            logWindowButton.triggered.connect(self.openLogViewerWin)

        helpButton = QtGui.QAction(QtGui.QIcon("data/assets/img/icon22.png"), "Help", self)
        helpButton.setShortcut("F1")
        helpButton.setStatusTip("Open the help window.")
        helpButton.triggered.connect(self.close)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        self.navButtonBack.setEnabled(False)
        navMenu.addAction(self.navButtonBack)
        self.navButtonForw.setEnabled(False)
        navMenu.addAction(self.navButtonForw)

        if config["debug"]["enableDebugMenu"]:
            debugMenu.addAction(logWindowButton)

        helpMenu.addAction(helpButton)

        ascvLogger.info("GUI has been initialized.")

    def dumpJson(self):
        with open("data/user/config.json", "w", encoding="utf-8") as cf:
            json.dump(config, cf, ensure_ascii=False, indent=4)

    # I should clean up these two functions below soon
    def openImage(self):
        self.imgFilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image File", "/", "Image files (*.jpg *.jpeg *.gif *.png *.bmp)")
        if self.imgFilePath != "":
            ascvLogger.info(f"Opened image. Image path: \"{self.imgFilePath}\"")
            self.dirPath_ = self.imgFilePath.replace(os.path.basename(self.imgFilePath), "")
            ascvLogger.info(f"Image's directory path: \"{self.dirPath_}\"")

            ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascvLogger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(1)
                else:
                    ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
                    self.imageNumber = self.dirImageList.index(self.imgFilePath) # note to self: clean this up
            else:
                ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)

            self.updateImage()

            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascvLogger.info("imgFilePath is empty!")

    def openDir(self):
        self.dirPath_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Open a Directory", "/")
        if self.dirPath_ != "":
            ascvLogger.info(f"Successfully opened directory, directory path is: \"{self.dirPath_}\"")

            ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascvLogger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(0)
                else:
                    ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
            else:
                ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(0)

            self.updateImage()
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascvLogger.info("dirPath_ is blank!")

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList = []

        for files in fileTypes:
            self.dirImageList.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList = [files.replace("\\", "/") for files in self.dirImageList]
        self.dirImageList.sort(key=str.lower)

        ascvLogger.info(f"Succesfully created dirImageList, dirImageList length: {len(self.dirImageList)}")
        ascvLogger.debug(f"dirImageList: {self.dirImageList}")

        if hasOpenedImage == 1:
            self.imageNumber = self.dirImageList.index(self.imgFilePath)
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]

    def updateImage(self):
        mwWidth = self.mainWidget.frameGeometry().width()
        mwHeight = self.mainWidget.frameGeometry().height()

        if self.imgFilePath != "":
            pixmap_ = QtGui.QPixmap(self.imgFilePath)
            pixmap = pixmap_.scaled(mwWidth, mwHeight, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(pixmap)
        self.label.resize(mwWidth, mwHeight)

    def resizeEvent(self, event):
        self.updateImage()

    # I should clean up these two too
    def prevImage(self):
        ascvLogger.debug(f"Showing previous image, imageNumber = {self.imageNumber}")
        self.imageNumber -= 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

    def nextImage(self):
        ascvLogger.debug(f"Showing next image, imageNumber = {self.imageNumber}")
        self.imageNumber += 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

    def openLogViewerWin(self):
        self.logViewerWin = LogViewer()
        self.logViewerWin.show()

    def onCloseActions(self):
        config["windowProperties"]["width"] = self.width()
        config["windowProperties"]["height"] = self.height()
        self.dumpJson()

    def closeEvent(self, event):
        if config["prompts"]["enableExitPrompt"]:
            reply = QtWidgets.QMessageBox(self)
            reply.setWindowIcon(QtGui.QIcon("data/assets/img/icon22.png"))
            reply.setWindowTitle("Exiting AscentViewer")
            reply.setText("<b>Are you sure you want to exit AscentViewer?</b>")
            reply.setInformativeText("<i>By the way, thank you for using this program!</i>")
            reply.setStandardButtons(QtWidgets.QMessageBox.StandardButtons.Yes | QtWidgets.QMessageBox.StandardButtons.No)
            checkbox = QtWidgets.QCheckBox("Do not show this again.")
            icon1 = QtGui.QPixmap("data/assets/img/door.png")
            icon = icon1.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            reply.setIconPixmap(QtGui.QPixmap(icon))
            reply.setCheckBox(checkbox)
            reply.setModal(True)

            x = reply.exec()

            if x == QtWidgets.QMessageBox.StandardButtons.Yes:
                print("Hello!")
                ascvLogger.info("Exiting...")
                self.onCloseActions()
                event.accept()
            else:
                ascvLogger.info("Not exiting.")
                event.ignore()

            if checkbox.isChecked():
                ascvLogger.info("Disabling prompt...")
                config["prompts"]["enableExitPrompt"] = False
            else:
                ascvLogger.info("Not disabling prompt.")

        else:
            ascvLogger.info("Exit prompt is disabled, exiting...")
            self.onCloseActions()
            event.accept()

class LogViewer(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.resize(600, 400)
        self.setWindowTitle("Log Viewer")
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon22.png"))

        logTextEdit = QtWidgets.QPlainTextEdit(self)
        logTextEdit.resize(600, 400)

        logTextEdit.appendPlainText("Coming soon.\n====================")

if __name__ == '__main__':
    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    ver = "early test version"
    date_format_file = "%d%m%Y_%H%M%S"
    date_format = "%d/%m/%Y %H:%M:%S"

    config = json.load(open("data/user/config.json")) # using json instead of qsettings, for now

    if config["temporary_files"]["logs"]["deleteLogsOnStartup"]:
        logs = glob.glob("data/user/temp/logs/*.txt")
        for f in logs:
            os.remove(f)
        print("Erased all logs.")
    else:
        print("Not deleting logs.")

    logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.txt"
    ascvLogger = logging.getLogger("AscV Logger")
    loggingLevel = getattr(logging, config["debug"]["logging"]["loggingLevel"])

    logging.basicConfig(level=loggingLevel, handlers=[logging.StreamHandler(), logging.FileHandler(logfile, "w", "utf-8")], format="[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s", datefmt=date_format) # thanks to Jan and several other sources for this
    if os.path.exists(logfile):
        with open(logfile, "w") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
            m = "="*15 + "[ BEGIN LOG ]" + "="*15
            f.write(f"{m}\n")
            print(m)

    ascvLogger.info(f"The OS is {platform.system()}.")

    if platform.system() == "Windows":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ascv") # makes the ascv icon appear in the taskbar, more info here: "https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105"

    signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")
    app = QtWidgets.QApplication(sys.argv)

    window = MainClass()
    window.show()
    window.statusBar().showMessage(f"Succesfully loaded. Version: {ver}")

    sys.exit(app.exec())

    # =================================
    # Thank you for using AscentViewer!
    # =================================
