# AscentViewer, a Python image viewer.
# Copyright (C) 2020-2021 DespawnedDiamond, A Crazy Town and other contributors
#
# This file is part of AscentViewer.
#
# AscentViewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AscentViewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AscentViewer.  If not, see <https://www.gnu.org/licenses/>.

# =====================================================
# Thank you for using and/or checking out AscentViewer!
# =====================================================

import sys
import json
import os
import platform
import signal
import glob
import shutil
import pkg_resources
import datetime
import logging

from PyQt5 import QtGui, QtCore, QtWidgets
from PIL import Image, ImageFont

from lib.headerlike import *

# from http://pantburk.info/?blog=77 and https://dzone.com/articles/python-custom-logging-handler-example
class CustomHandler(logging.StreamHandler):
    def __init__(self, statusBar):
        '''
        The custom logging handler for the QStatusBar.
        '''
        logging.Handler.__init__(self)
        self.statusBar = statusBar

    def emit(self, record):
        self.statusBar.showMessage(self.format(record))

        if record.levelname == "WARNING":
            self.statusBar.setStyleSheet("background: #EBCB8B; color: black;")
        elif record.levelname == "ERROR":
            self.statusBar.setStyleSheet("background: #D08770; color: black;")
        elif record.levelname == "CRITICAL":
            self.statusBar.setStyleSheet("background: #BF616A;")

    def flush(self):
        pass

class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        '''
        The core AscentViewer function. It sets up the UI, as well as some other things.
        '''
        super().__init__()

        # =====================================================
        # non-gui related stuff:

        self.dirPath = ""
        self.imgFilePath = ""
        self.saveConfigOnExit = True
        sys.excepthook = self.except_hook # https://stackoverflow.com/a/33741755/14558305

        # from http://pantburk.info/?blog=77. This code allows the status bar to show warning messages from loggers
        customHandler = CustomHandler(self.statusBar())
        customHandler.setLevel(logging.WARN)

        formatter = logging.Formatter("%(levelname)s: %(message)s")
        customHandler.setFormatter(formatter)

        ascvLogger.addHandler(customHandler)

        # =====================================================
        # gui related stuff:

        ascvLogger.info("Initializing GUI.")
        # from https://stackoverflow.com/questions/27955654/how-to-use-non-standard-custom-font-with-stylesheets
        selawikFonts = glob.glob("data/assets/fonts/selawik/*.ttf")
        for f in selawikFonts:
            f = f.replace("\\", "/")
            QtGui.QFontDatabase.addApplicationFont(f)
        _ = QtGui.QFont("Selawik Bold") # this PROBABLY fixes an issue with KDE's Plasma where the font wouldn't display correctly

        if config["hellMode"]: # just a funny easter egg
            mainFont = QtGui.QFont("Selawik")
            mainFont.setBold(True)
            mainFont.setItalic(True)
            mainFont.setPointSize(32)
            QtWidgets.QApplication.setFont(mainFont)
        elif platform.system() == "Windows":
            # Segoe UI is better than the default font, and is included with the latest versions of Windows (starting from Vista(?))
            mainFont = QtGui.QFont("Segoe UI")
            mainFont.setPointSize(9)
            QtWidgets.QApplication.setFont(mainFont)

        self.setWindowTitle(f"AscentViewer")
        self.resize(config["windowProperties"]["width"], config["windowProperties"]["height"])
        self.move(config["windowProperties"]["x"], config["windowProperties"]["y"])
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        self.statusBar().setStyleSheet("background: #777CC1;")

        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)

        vBox = QtWidgets.QVBoxLayout(self.mainWidget)
        vBox.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel()
        self.label.setText(localization["mainUiElements"]["openImgFileText"])
        self.label.setStyleSheet("color: white; background: #2E3440;")
        self.label.setMinimumSize(16, 16)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        mainLabelFont = QtGui.QFont("Selawik", 32)
        mainLabelFont.setBold(True)
        self.label.setFont(mainLabelFont)

        # https://stackoverflow.com/a/34802367/14558305
        self.label.resizeEvent = (lambda old_method: (lambda event: (self.updateFunction(), old_method(event))[-1]))(self.label.resizeEvent)

        self.bottom = QtWidgets.QFrame()
        self.bottom.setMinimumHeight(90)
        self.bottom.setMaximumHeight(200)
        self.bottom.setContentsMargins(0, 0, 0, 0)
        self.bottom.setStyleSheet("background: #525685;")

        btHBox = QtWidgets.QHBoxLayout(self.bottom)

        self.detailsFileIcon = QtWidgets.QLabel()
        icon_ = QtGui.QPixmap("data/assets/img/icon3.png")
        icon = icon_.scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.detailsFileIcon.setPixmap(QtGui.QPixmap(icon))

        self.fileLabel = QtWidgets.QLabel()
        self.fileLabel.setStyleSheet("color: white;")
        fileLabelFont = QtGui.QFont("Selawik", 14)
        fileLabelFont.setBold(True)
        self.fileLabel.setFont(fileLabelFont)
        self.fileLabel.setText(localization["mainUiElements"]["panelText"])

        self.dateModifiedLabel = QtWidgets.QLabel()
        self.dateModifiedLabel.setStyleSheet("color: white;")

        self.dimensionsLabel = QtWidgets.QLabel()
        self.dimensionsLabel.setStyleSheet("color: white;")

        btFileInfoVBox1Frame = QtWidgets.QFrame()
        btFileInfoVBox1 = QtWidgets.QVBoxLayout(btFileInfoVBox1Frame)
        btFileInfoVBox1.setContentsMargins(0, 0, 0, 0)
        btFileInfoVBox1.setAlignment(QtCore.Qt.AlignLeft)
        btFileInfoVBox1.addWidget(self.dateModifiedLabel)
        btFileInfoVBox1.addWidget(self.dimensionsLabel)

        btFileInfoContainerHBoxFrame = QtWidgets.QFrame() # A really long name, I know
        btFileInfoContainerHBox = QtWidgets.QHBoxLayout(btFileInfoContainerHBoxFrame)
        btFileInfoContainerHBox.setContentsMargins(0, 0, 0, 0)
        btFileInfoContainerHBox.setAlignment(QtCore.Qt.AlignLeft)
        btFileInfoContainerHBox.addWidget(btFileInfoVBox1Frame)

        btMainVBoxFrame = QtWidgets.QFrame()
        btMainVBox = QtWidgets.QVBoxLayout(btMainVBoxFrame)
        btMainVBox.setAlignment(QtCore.Qt.AlignTop)
        btMainVBox.setContentsMargins(0, 0, 0, 0)
        btMainVBox.addWidget(self.fileLabel)
        btMainVBox.addWidget(btFileInfoContainerHBoxFrame)

        btHBox.setAlignment(QtCore.Qt.AlignLeft) # This probably won't work in PyQt6
        btHBox.addWidget(self.detailsFileIcon)
        btHBox.addWidget(btMainVBoxFrame)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.label)
        splitter.addWidget(self.bottom)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 1)
        splitter.setSizes([1, config["windowProperties"]["bottomSplitterPanelH"]])
        splitter.setStyleSheet("QSplitter::handle{background: #777CC1; height: 2;}")

        vBox.addWidget(splitter)

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["file"]["title"])
        navMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["navigation"]["title"])
        toolsMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["tools"]["title"])
        if config["debug"]["enableDebugMenu"]:
            debugMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["debug"]["title"])
        helpMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["help"]["title"])

        openImgButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/file.png"), localization["mainUiElements"]["menuBar"]["file"]["openImgText"], self)
        openImgButton.setShortcut("CTRL+O")
        openImgButton.setStatusTip("Open an image file")
        openImgButton.triggered.connect(self.openImage)

        openDirButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/file.png"), localization["mainUiElements"]["menuBar"]["file"]["openDirText"], self)
        openDirButton.setShortcut("CTRL+Shift+O")
        openDirButton.setStatusTip("Open a directory file")
        openDirButton.triggered.connect(self.openDir)

        exitButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/door.png"), localization["mainUiElements"]["menuBar"]["file"]["exitText"], self)
        exitButton.setShortcut("CTRL+Q")
        exitButton.setStatusTip("Exit application")
        exitButton.triggered.connect(self.close)

        self.navButtonBack = QtWidgets.QAction(QtGui.QIcon(), localization["mainUiElements"]["menuBar"]["navigation"]["back"], self)
        self.navButtonBack.setShortcut("Left")
        self.navButtonBack.setStatusTip("Go to previous image in directory")
        self.navButtonBack.triggered.connect(self.prevImage)
        self.navButtonBack.setEnabled(False)

        self.navButtonForw = QtWidgets.QAction(QtGui.QIcon(), localization["mainUiElements"]["menuBar"]["navigation"]["forw"], self)
        self.navButtonForw.setShortcut("Right")
        self.navButtonForw.setStatusTip("Go to next image in directory")
        self.navButtonForw.triggered.connect(self.nextImage)
        self.navButtonForw.setEnabled(False)

        if config["debug"]["enableDebugMenu"]:
            logWindowButton = QtWidgets.QAction(QtGui.QIcon(), "Log Viewer", self)
            logWindowButton.setShortcut("CTRL+Shift+L")
            logWindowButton.setStatusTip("Open the log viewer window.")
            logWindowButton.triggered.connect(self.openLogWin)

            dummyException = QtWidgets.QAction(QtGui.QIcon(), "Raise dummy exception", self)
            dummyException.setShortcut("CTRL+Shift+F10")
            dummyException.setStatusTip("Raise a dummy exception")
            dummyException.triggered.connect(self.dummyExceptionFunc)

        resetCfg = QtWidgets.QAction(QtGui.QIcon(), "Reset config", self)
        resetCfg.setShortcut("CTRL+Shift+F9")
        resetCfg.setStatusTip("Reset the configuration file.")
        resetCfg.triggered.connect(self.resetConfigDialog)

        helpButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/icon3.png"), "Help", self)
        helpButton.setShortcut("F1")
        helpButton.setStatusTip("Open the help window.")
        helpButton.triggered.connect(self.openHelpWin)

        aboutButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/icon3.png"), "About", self)
        aboutButton.setShortcut("Shift+F1")
        aboutButton.setStatusTip("Open the about window.")
        aboutButton.triggered.connect(self.openAboutWin)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        navMenu.addAction(self.navButtonBack)
        navMenu.addAction(self.navButtonForw)

        if config["debug"]["enableDebugMenu"]:
            debugMenu.addAction(logWindowButton)
            debugMenu.addAction(dummyException)

        toolsMenu.addAction(resetCfg)

        helpMenu.addAction(helpButton)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutButton)

        self.label.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.label.addAction(openImgButton)

        self.statusBar().showMessage(localization["mainUiElements"]["statusBar"]["greetMessageBeginning"] + ver)
        ascvLogger.info("GUI has been initialized.")

    # ISSUE: for some images, this REALLY makes the program lag
    # the foundation of the code comes from https://stackoverflow.com/a/43570124/14558305
    def updateFunction(self):
        '''
        A function that, well, updates. Updates widgets, to be more exact.
        '''

        mwWidth = self.label.frameGeometry().width()
        mwHeight = self.label.frameGeometry().height()

        if self.imgFilePath != "":
            # should probably not use Pillow for this, might change this later
            # from https://stackoverflow.com/questions/6444548/how-do-i-get-the-picture-size-with-pil
            im = Image.open(self.imgFilePath)

            pixmap_ = QtGui.QPixmap(self.imgFilePath)
            pixmap = pixmap_.scaled(mwWidth, mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)

            dateModified = datetime.datetime.fromtimestamp(os.path.getmtime(self.imgFilePath)).strftime(date_format)
            imWidth, imHeight = im.size
            dimensions = f"{imWidth}x{imHeight}"

            self.fileLabel.setText(os.path.basename(self.imgFilePath))
            self.dateModifiedLabel.setText(f"<b>Date modified:</b> {dateModified}")
            self.dimensionsLabel.setText(f"<b>Dimensions:</b> {dimensions}")

            icon_ = QtGui.QPixmap("data/assets/img/file.png")
            icon = icon_.scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.detailsFileIcon.setPixmap(QtGui.QPixmap(icon))

            self.label.resize(mwWidth, mwHeight)

    def resetConfigDialog(self):
        '''
        A function that shows a dialog that asks the user if they want to reset the configuration file
        (copy config.json from default_config to the user folder). If they respond with "Yes", the function
        resets the configuration to its defaults.
        '''
        reply = QtWidgets.QMessageBox(self)
        reply.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))
        reply.setWindowTitle("Reset configuration")
        reply.setText("<b>Are you sure you want to reset the configuration file?</b>")
        reply.setInformativeText("<i>This will also prevent the program saving the config file on exit for this session.</i>")
        reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        checkbox = QtWidgets.QCheckBox("After resetting, exit the program.")
        icon_ = QtGui.QPixmap("data/assets/img/icon3.png")
        icon = icon_.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        reply.setIconPixmap(QtGui.QPixmap(icon))
        reply.setCheckBox(checkbox)
        reply.setModal(True)

        x = reply.exec_()

        if checkbox.isChecked():
            config["prompts"]["enableExitPrompt"] = False
            self.onCloseActions()
            self.close()

        if x == QtWidgets.QMessageBox.Yes:
            shutil.copyfile("data/assets/default_config/config.json", "data/user/config.json")
            self.saveConfigOnExit = False

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
                    self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)
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
        else:
            ascvLogger.info("dirPath_ is blank!")

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList_ = []

        for files in fileTypes:
            self.dirImageList_.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList_ = [files.replace("\\", "/") for files in self.dirImageList_]
        self.dirImageList_.sort(key=str.lower)

        if len(self.dirImageList_) != 0:
            ascvLogger.info(f"Succesfully created dirImageList_. It's not empty.")
            ascvLogger.debug(f"dirImageList_: {self.dirImageList_}")
            ascvLogger.info(f"dirImageList_ length: {len(self.dirImageList_)}")
            ascvLogger.info(f"Setting dirImageList to dirImageList_")

            self.dirImageList = self.dirImageList_

            if hasOpenedImage == 1:
                self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                self.imageNumber = 0

            self.imgFilePath = self.dirImageList[self.imageNumber]

            self.updateFunction()
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascvLogger.info(f"Succesfully created dirImageList_, but it's empty! Not setting dirImageList to dirImageList_")

    # I should clean up these two too
    def prevImage(self):
        ascvLogger.debug(f"Showing previous image, imageNumber = {self.imageNumber}")
        if self.imageNumber != 0:
            self.imageNumber -= 1
        else:
            self.imageNumber = len(self.dirImageList) - 1

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction()

    def nextImage(self):
        ascvLogger.debug(f"Showing next image, imageNumber = {self.imageNumber}")
        if self.imageNumber != len(self.dirImageList) - 1:
            self.imageNumber += 1
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction()

    def dumpJson(self):
        with open("data/user/config.json", "w", encoding="utf-8", newline="\n") as cf:
            json.dump(config, cf, ensure_ascii=False, indent=4)
            cf.write("\n") # https://codeyarns.com/tech/2017-02-22-python-json-dump-misses-last-newline.html

    def onCloseActions(self):
        config["windowProperties"]["width"] = self.width()
        config["windowProperties"]["height"] = self.height()
        config["windowProperties"]["x"] = self.x()
        config["windowProperties"]["y"] = self.y()
        config["windowProperties"]["bottomSplitterPanelH"] = self.bottom.height()

        if self.saveConfigOnExit == True:
            self.dumpJson()

    def closeEvent(self, event):
        if config["prompts"]["enableExitPrompt"]:
            reply = QtWidgets.QMessageBox(self)
            reply.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))
            reply.setWindowTitle("Exiting AscentViewer")
            reply.setText("<b>Are you sure you want to exit AscentViewer?</b>")
            reply.setInformativeText("<i>By the way, thank you for using this program!</i>")
            reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            checkbox = QtWidgets.QCheckBox("Do not show this again.")
            icon_ = QtGui.QPixmap("data/assets/img/door.png")
            icon = icon_.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            reply.setIconPixmap(QtGui.QPixmap(icon))
            reply.setCheckBox(checkbox)
            reply.setModal(True)

            x = reply.exec_()

            if checkbox.isChecked():
                ascvLogger.info("Disabling prompt...")
                config["prompts"]["enableExitPrompt"] = False
            else:
                ascvLogger.info("Not disabling prompt.")

            if x == QtWidgets.QMessageBox.Yes:
                ascvLogger.info("Exiting...")
                self.onCloseActions()
                event.accept()
            else:
                ascvLogger.info("Not exiting.")
                event.ignore()

        else:
            ascvLogger.info("Exit prompt is disabled, exiting...")
            self.onCloseActions()
            event.accept()

    # from https://stackoverflow.com/a/33741755/14558305
    # bookmark: https://stackoverflow.com/questions/6598053/python-global-exception-handling
    def except_hook(self, cls, exception, traceback): # note: implement this in ascv.py somehow
        # custom except hook
        ascvLogger.critical(f"An exception occured: \"{exception}\" | Saving settings in case of a fatal issue...")
        sys.__excepthook__(cls, exception, traceback)
        self.onCloseActions()

    def dummyExceptionFunc(self):
        raise Exception("Dummy exception!")

    def openLogWin(self):
        # not using a modal QDialog (like the About window) here because I want this window to be non-modal
        logViewer = QtWidgets.QMainWindow(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        logViewer.resize(600, 400)
        geo = logViewer.geometry()
        geo.moveCenter(self.geometry().center())
        logViewer.setGeometry(geo)

        logViewer.setWindowTitle("Log Viewer")
        logViewer.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))
        logViewer.setAttribute(QtCore.Qt.WA_QuitOnClose, True) # https://stackoverflow.com/questions/16468584/qwidget-doesnt-close-when-main-window-is-closed

        logTextEdit = QtWidgets.QPlainTextEdit(logViewer)
        logViewer.setCentralWidget(logTextEdit)
        logTextEdit.appendPlainText("Coming soon.")

        logViewer.show()

    def openHelpWin(self):
        helpWin = QtWidgets.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        helpWin.resize(725, 460)

        helpWin.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        helpWin.setModal(True)
        helpWin.setWindowTitle("Help")
        helpWin.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        helpWin.label = QtWidgets.QLabel()
        helpWin.label.setText("<b>Coming soon.</b><br /><i>In the meantime, check out the repository's Wiki.</i>")

        helpWin.gridLayout = QtWidgets.QGridLayout(helpWin)
        helpWin.gridLayout.addWidget(helpWin.label)

        mainLabelFont = QtGui.QFont()
        mainLabelFont.setPointSize(16)
        helpWin.label.setFont(mainLabelFont)

        helpWin.label.setAlignment(QtCore.Qt.AlignCenter)

        helpWin.show()

    def openAboutWin(self):
        about = QtWidgets.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        # =====================================================
        # This code below is a modified version of about.py (located in the misc folder, 
        # that's located in the source folder of the repository), a script that was generated by pyuic5.
        # That is why the entire thing is big and clunky.

        about.resize(900, 502)
        about.setObjectName("about")
        about.setModal(True)
        about.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))
        about.gridLayout = QtWidgets.QGridLayout(about)
        about.gridLayout.setContentsMargins(0, 0, 0, 0)
        about.gridLayout.setObjectName("gridLayout")
        about.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        about.horizontalLayout_3.setContentsMargins(9, 9, 9, 9)
        about.horizontalLayout_3.setSpacing(9)
        about.horizontalLayout_3.setObjectName("horizontalLayout_3")
        about.verticalLayout_4 = QtWidgets.QVBoxLayout()
        about.verticalLayout_4.setObjectName("verticalLayout_4")
        about.image = QtWidgets.QLabel(about)
        about.image.setMinimumSize(QtCore.QSize(300, 300))
        about.image.setMaximumSize(QtCore.QSize(300, 300))
        about.image.setText("")
        about.image.setPixmap(QtGui.QPixmap("data/assets/img/icon3.png"))
        about.image.setScaledContents(True)
        about.image.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        about.image.setWordWrap(False)
        about.image.setObjectName("image")
        about.verticalLayout_4.addWidget(about.image, 0, QtCore.Qt.AlignTop)
        about.horizontalLayout_3.addLayout(about.verticalLayout_4)
        about.widget = QtWidgets.QWidget(about)
        about.widget.setObjectName("widget")
        about.verticalLayout_3 = QtWidgets.QVBoxLayout(about.widget)
        about.verticalLayout_3.setSpacing(4)
        about.verticalLayout_3.setObjectName("verticalLayout_3")
        about.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        about.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        about.horizontalLayout_5.setObjectName("horizontalLayout_5")
        about.programName = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        about.programName.setFont(font)
        about.programName.setTextFormat(QtCore.Qt.PlainText)
        about.programName.setScaledContents(False)
        about.programName.setObjectName("programName")
        about.horizontalLayout_5.addWidget(about.programName)
        spacerItem = QtWidgets.QSpacerItem(8, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        about.horizontalLayout_5.addItem(spacerItem)
        about.majorReleaseName = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik Semilight")
        font.setPointSize(36)
        about.majorReleaseName.setFont(font)
        about.majorReleaseName.setStyleSheet("color: #8FBCBB;")
        about.majorReleaseName.setTextFormat(QtCore.Qt.PlainText)
        about.majorReleaseName.setObjectName("majorReleaseName")
        about.horizontalLayout_5.addWidget(about.majorReleaseName)
        about.horizontalLayout_5.setStretch(2, 1)
        about.verticalLayout_3.addLayout(about.horizontalLayout_5)
        about.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        about.horizontalLayout_8.setObjectName("horizontalLayout_8")
        about.versionLabel = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik Semilight")
        font.setPointSize(20)
        about.versionLabel.setFont(font)
        about.versionLabel.setObjectName("versionLabel")
        about.horizontalLayout_8.addWidget(about.versionLabel)
        spacerItem1 = QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        about.horizontalLayout_8.addItem(spacerItem1)
        about.version = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik Light")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        about.version.setFont(font)
        about.version.setStyleSheet("color: #8FBCBB;")
        about.version.setTextFormat(QtCore.Qt.RichText)
        about.version.setObjectName("version")
        about.horizontalLayout_8.addWidget(about.version)
        about.horizontalLayout_8.setStretch(2, 1)
        about.verticalLayout_3.addLayout(about.horizontalLayout_8)
        about.line = QtWidgets.QFrame(about.widget)
        about.line.setMinimumSize(QtCore.QSize(0, 22))
        about.line.setStyleSheet("color: #4C566A;")
        about.line.setFrameShadow(QtWidgets.QFrame.Plain)
        about.line.setFrameShape(QtWidgets.QFrame.HLine)
        about.line.setObjectName("line")
        about.verticalLayout_3.addWidget(about.line)
        about.verticalLayout_5 = QtWidgets.QVBoxLayout()
        about.verticalLayout_5.setContentsMargins(-1, 0, -1, -1)
        about.verticalLayout_5.setSpacing(4)
        about.verticalLayout_5.setObjectName("verticalLayout_5")
        about.horizontalLayout = QtWidgets.QHBoxLayout()
        about.horizontalLayout.setObjectName("horizontalLayout")
        about.label = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        about.label.setFont(font)
        about.label.setTextFormat(QtCore.Qt.PlainText)
        about.label.setObjectName("label")
        about.horizontalLayout.addWidget(about.label)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        about.horizontalLayout.addItem(spacerItem2)
        about.label_9 = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        about.label_9.setFont(font)
        about.label_9.setTextFormat(QtCore.Qt.PlainText)
        about.label_9.setObjectName("label_9")
        about.horizontalLayout.addWidget(about.label_9)
        about.verticalLayout_5.addLayout(about.horizontalLayout)
        about.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        about.horizontalLayout_2.setObjectName("horizontalLayout_2")
        about.label_2 = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        about.label_2.setFont(font)
        about.label_2.setTextFormat(QtCore.Qt.PlainText)
        about.label_2.setObjectName("label_2")
        about.horizontalLayout_2.addWidget(about.label_2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        about.horizontalLayout_2.addItem(spacerItem3)
        about.label_10 = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        about.label_10.setFont(font)
        about.label_10.setTextFormat(QtCore.Qt.PlainText)
        about.label_10.setObjectName("label_10")
        about.horizontalLayout_2.addWidget(about.label_10)
        about.verticalLayout_5.addLayout(about.horizontalLayout_2)
        about.verticalLayout_3.addLayout(about.verticalLayout_5)
        about.line_2 = QtWidgets.QFrame(about.widget)
        about.line_2.setMinimumSize(QtCore.QSize(0, 22))
        about.line_2.setStyleSheet("color: #4C566A;")
        about.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        about.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        about.line_2.setObjectName("line_2")
        about.verticalLayout_3.addWidget(about.line_2)
        about.label_11 = QtWidgets.QLabel(about.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(12)
        about.label_11.setFont(font)
        about.label_11.setTextFormat(QtCore.Qt.MarkdownText)
        about.label_11.setScaledContents(False)
        about.label_11.setWordWrap(True)
        about.label_11.setIndent(-1)
        about.label_11.setOpenExternalLinks(True)
        about.label_11.setObjectName("label_11")
        about.verticalLayout_3.addWidget(about.label_11)
        about.horizontalLayout_3.addWidget(about.widget, 0, QtCore.Qt.AlignTop)
        about.horizontalLayout_3.setStretch(1, 1)
        about.gridLayout.addLayout(about.horizontalLayout_3, 0, 0, 1, 1)
        about.verticalWidget = QtWidgets.QWidget(about)
        about.verticalWidget.setMaximumSize(QtCore.QSize(16777215, 96))
        about.verticalWidget.setStyleSheet("background:#3B4252;")
        about.verticalWidget.setObjectName("verticalWidget")
        about.verticalLayout_7 = QtWidgets.QVBoxLayout(about.verticalWidget)
        about.verticalLayout_7.setObjectName("verticalLayout_7")
        about.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        about.horizontalLayout_4.setContentsMargins(24, 24, 24, 24)
        about.horizontalLayout_4.setSpacing(24)
        about.horizontalLayout_4.setObjectName("horizontalLayout_4")
        about.widget1 = QtWidgets.QWidget(about.verticalWidget)
        about.widget1.setObjectName("widget1")
        about.horizontalLayout_7 = QtWidgets.QHBoxLayout(about.widget1)
        about.horizontalLayout_7.setObjectName("horizontalLayout_7")
        about.label_5 = QtWidgets.QLabel(about.widget1)
        about.label_5.setMinimumSize(QtCore.QSize(16, 16))
        about.label_5.setMaximumSize(QtCore.QSize(16, 16))
        about.label_5.setText("")
        about.label_5.setTextFormat(QtCore.Qt.PlainText)
        about.label_5.setPixmap(QtGui.QPixmap("data/assets/img/GitHub-Mark/PNG/GitHub-Mark-Light-32px.png"))
        about.label_5.setScaledContents(True)
        about.label_5.setObjectName("label_5")
        about.horizontalLayout_7.addWidget(about.label_5)
        about.label_4 = QtWidgets.QLabel(about.widget1)
        about.label_4.setMinimumSize(QtCore.QSize(16, 16))
        about.label_4.setTextFormat(QtCore.Qt.RichText)
        about.label_4.setScaledContents(False)
        about.label_4.setOpenExternalLinks(True)
        about.label_4.setObjectName("label_4")
        about.horizontalLayout_7.addWidget(about.label_4)
        about.horizontalLayout_4.addWidget(about.widget1, 0, QtCore.Qt.AlignHCenter)
        about.widget2 = QtWidgets.QWidget(about.verticalWidget)
        about.widget2.setObjectName("widget2")
        about.horizontalLayout_6 = QtWidgets.QHBoxLayout(about.widget2)
        about.horizontalLayout_6.setObjectName("horizontalLayout_6")
        about.label_3 = QtWidgets.QLabel(about.widget2)
        about.label_3.setMinimumSize(QtCore.QSize(16, 16))
        about.label_3.setMaximumSize(QtCore.QSize(16, 16))
        about.label_3.setText("")
        about.label_3.setTextFormat(QtCore.Qt.PlainText)
        about.label_3.setPixmap(QtGui.QPixmap("data/assets/img/Material-Icons/public-white-18dp/1x/baseline_public_white_18dp.png"))
        about.label_3.setScaledContents(True)
        about.label_3.setObjectName("label_3")
        about.horizontalLayout_6.addWidget(about.label_3)
        about.label_6 = QtWidgets.QLabel(about.widget2)
        about.label_6.setMinimumSize(QtCore.QSize(16, 16))
        about.label_6.setTextFormat(QtCore.Qt.RichText)
        about.label_6.setScaledContents(False)
        about.label_6.setOpenExternalLinks(True)
        about.label_6.setObjectName("label_6")
        about.horizontalLayout_6.addWidget(about.label_6)
        about.horizontalLayout_4.addWidget(about.widget2, 0, QtCore.Qt.AlignHCenter)
        about.verticalLayout_7.addLayout(about.horizontalLayout_4)
        about.gridLayout.addWidget(about.verticalWidget, 1, 0, 1, 1)

        _translate = QtCore.QCoreApplication.translate
        about.setWindowTitle(_translate("Form", "About"))
        about.programName.setText(_translate("Form", "AscentViewer"))
        about.majorReleaseName.setText(_translate("Form", "Cobalt"))
        about.versionLabel.setText(_translate("Form", "version"))
        about.version.setText(_translate("Form", ver))
        about.label.setText(_translate("Form", "Python version"))
        try:
            about.label_9.setText(_translate("Form", platform.python_version()))
        except:
            about.label_9.setText(_translate("Form", "unknown"))
        about.label_2.setText(_translate("Form", "PyQt5 version"))
        try:
            about.label_10.setText(_translate("Form", pkg_resources.get_distribution("PyQt5").version))
        except:
            about.label_10.setText(_translate("Form", "unknown"))
        about.label_11.setText(_translate("Form", "**AscentViewer** is an image viewer written in [**Python**](https://www.python.org/) based on [**PyQt**](https://riverbankcomputing.com/software/pyqt/) and several other libraries."))
        about.label_4.setText(_translate("Form", "<a href=\"https://github.com/despawnedd/AscentViewer/\">GitHub repository</a>"))
        about.label_6.setText(_translate("Form", "<a href=\"https://dd.acrazytown.com/AscentViewer/\">Website</a>"))

        about.exec_()

# from https://stackoverflow.com/a/31688396/14558305 and https://stackoverflow.com/a/39215961/14558305
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

if __name__ == "__main__":
    # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    ver = "0.0.1_dev-3.0-PyQt5"
    date_format_file = "%d%m%Y_%H%M%S"
    date_format = "%d/%m/%Y %H:%M:%S"

    config = json.load(open("data/user/config.json", encoding="utf-8")) # using json instead of QSettings, for now
    lang = config["localization"]["lang"]
    localization = json.load(open(f"data/assets/localization/lang/{lang}.json", encoding="utf-8"))
    logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.log"

    print("Deleting logs on statup is ", end="")
    if config["temporary_files"]["logs"]["deleteLogsOnStartup"]:
        print("enabled, erasing all logs...")
        logs = glob.glob("data/user/temp/logs/log*.log")
        for f in logs:
            os.remove(f)
    else:
        print("disabled, not deleting logs.")

    # thanks to Jan and several other sources for this
    loggingLevel = getattr(logging, config["debug"]["logging"]["loggingLevel"])
    logging.basicConfig(level=loggingLevel,
                        handlers=[logging.StreamHandler(), logging.FileHandler(logfile, "a", "utf-8")],
                        format="[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s",
                        datefmt=date_format)

    ascvLogger = logging.getLogger("Main logger")
    stderrLogger = logging.getLogger("stderr logger")
    sys.stderr = StreamToLogger(stderrLogger, logging.ERROR)

    with open(logfile, "a") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
        logIntroLine = "="*20 + "[ BEGIN LOG ]" + "="*20
        f.write(f"{logIntroLine}\n")
    print(logIntroLine)

    ascvLogger.info(f"Arguments: {sys.argv}")

    if platform.system() == "Windows":
        # makes the AscentViewer icon appear in the taskbar, more info here: "https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105"
        # (newer comamnd gotten from 15-minute-apps: "https://github.com/learnpyqt/15-minute-apps")
        from PyQt5 import QtWinExtras
        QtWinExtras.QtWin.setCurrentProcessExplicitAppUserModelID(f"DespawnedDiamond.AscentViewer.ascv.{ver}")

    if platform.system() == "Linux":
        # just a fun little piece of code that prints out your distro name and version
        import distro
        distroName = " ".join(distro.linux_distribution()).title()
        ascvLogger.info(f"The OS is {platform.system()} ({distroName}).")
    else:
        ascvLogger.info(f"The OS is {platform.system()}.")

    # start the actual program
    app = QtWidgets.QApplication(sys.argv)

    # based on https://gist.github.com/QuantumCD/6245215 and https://www.nordtheme.com/docs/colors-and-palettes
    app.setStyle("Fusion")
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(46, 52, 64))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(38, 43, 53)) #59, 66, 82; 34, 38, 47
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(46, 52, 64))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(34, 38, 47))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(191, 97, 106))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(129, 161, 193))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(119, 124, 193))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = MainUi()
    window.show()

    sys.exit(app.exec_())
