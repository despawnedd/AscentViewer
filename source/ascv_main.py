from PyQt5 import QtGui, QtCore, QtWidgets
import json
import glob
import os
import shutil
import resources

try:
    os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
except:
    pass

ver = "0.0.1_dev-2.1-PyQt5"
config = json.load(open("data/user/config.json", encoding="utf-8"))

lang = config["localization"]["lang"]
localization = json.load(open(f"data/assets/localization/lang/{lang}.json", encoding="utf-8"))

class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # non-gui related stuff:

        #ascvLogger.info("Initializing GUI.")
        self.dirPath = ""
        self.imgFilePath = ""
        self.saveConfigOnExit = True

        # gui related stuff:

        # from https://stackoverflow.com/questions/27955654/how-to-use-non-standard-custom-font-with-stylesheets
        selawikFonts = glob.glob("data/assets/fonts/selawik/*.ttf")
        for f in selawikFonts:
            f = f.replace("\\", "/")
            QtGui.QFontDatabase.addApplicationFont(f)

        if config["hellMode"]: # just a funny easter egg
            mainFont = QtGui.QFont("Selawik")
            mainFont.setBold(True)
            mainFont.setItalic(True)
            mainFont.setPointSize(32)
            QtWidgets.QApplication.setFont(mainFont)

        self.setWindowTitle(f"AscentViewer {ver}")
        self.resize(config["windowProperties"]["width"], config["windowProperties"]["height"])
        self.move(config["windowProperties"]["x"], config["windowProperties"]["y"])
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        self.statusBar().setStyleSheet("background: #777CC1; color: white;")

        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)

        vBox = QtWidgets.QVBoxLayout(self.mainWidget)
        vBox.setContentsMargins(0, 0, 0, 0)

        self.bottom = QtWidgets.QFrame()
        self.bottom.setMinimumHeight(80)
        self.bottom.setMaximumHeight(150)
        self.bottom.setContentsMargins(0, 0, 0, 0)
        self.bottom.setStyleSheet("background: #525685;")

        bthBox = QtWidgets.QHBoxLayout(self.bottom)
        bthBox.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel()
        self.label.setText(localization["mainUiElements"]["openImgFileText"])
        self.label.setStyleSheet("color: white; background: #2E3440;")
        self.label.setMinimumSize(16, 16)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        mainLabelFont = QtGui.QFont("Selawik")
        mainLabelFont.setBold(True)
        mainLabelFont.setPointSize(32)
        self.label.setFont(mainLabelFont)
        #self.label.setWhatsThis("Main image label")

        csIcon = QtWidgets.QLabel()
        icon_ = QtGui.QPixmap("data/assets/img/icon3.png")
        icon = icon_.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        csIcon.setPixmap(QtGui.QPixmap(icon))

        self.csLabel = QtWidgets.QLabel()
        self.csLabel.setText(localization["mainUiElements"]["comingSoonPanelText"])
        self.csLabel.setStyleSheet("color: white;")
        self.csLabelFont = QtGui.QFont("Selawik")
        self.csLabelFont.setPointSize(16)
        self.csLabel.setFont(self.csLabelFont)

        bthBox.addWidget(csIcon)
        bthBox.addWidget(self.csLabel)

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

        if config["debug"]["enableDebugMenu"]:
            debugMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["debug"]["title"])

        toolsMenu = mainMenu.addMenu(localization["mainUiElements"]["menuBar"]["tools"]["title"])

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

        resetCfg = QtWidgets.QAction(QtGui.QIcon(), "Reset config", self)
        resetCfg.setShortcut("CTRL+Shift+F9")
        resetCfg.setStatusTip("Reset the configuration file.")
        resetCfg.triggered.connect(self.resetConfigFunc)

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

        toolsMenu.addAction(resetCfg)

        helpMenu.addAction(helpButton)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutButton)

        self.mainWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.mainWidget.addAction(openImgButton)

        self.statusBar().showMessage(localization["mainUiElements"]["statusBar"]["greetMessageBeginning"] + ver)
        #ascvLogger.info("GUI has been initialized.")

    def dumpJson(self):
        with open("data/user/config.json", "w", encoding="utf-8") as cf:
            json.dump(config, cf, ensure_ascii=False, indent=4)

    def resetConfigFunc(self):
        reply = QtWidgets.QMessageBox(self)
        reply.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))
        reply.setWindowTitle("Reset config")
        reply.setText("<b>Are you sure you want to reset the configuration file?</b>")
        reply.setInformativeText("<i>This will also prevent the program from dumping the config file on exit for this session.</i>")
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
            #ascvLogger.info(f"Opened image. Image path: \"{self.imgFilePath}\"")
            self.dirPath_ = self.imgFilePath.replace(os.path.basename(self.imgFilePath), "")
            #ascvLogger.info(f"Image's directory path: \"{self.dirPath_}\"")

            #ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                #ascvLogger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    #ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(1)
                else:
                    #ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
                    self.imageNumber = self.dirImageList.index(self.imgFilePath) # note to self: clean this up
            else:
                #ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)

            self.updateImage()

            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        #else:
        #    #ascvLogger.info("imgFilePath is empty!")

    def openDir(self):
        self.dirPath_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Open a Directory", "/")
        if self.dirPath_ != "":
            #ascvLogger.info(f"Successfully opened directory, directory path is: \"{self.dirPath_}\"")

            #ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                #ascvLogger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    #ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(0)
                #else:
                #    #ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
            else:
                #ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(0)

            self.updateImage()
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        #else:
        #    #ascvLogger.info("dirPath_ is blank!")

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList = []

        for files in fileTypes:
            self.dirImageList.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList = [files.replace("\\", "/") for files in self.dirImageList]
        self.dirImageList.sort(key=str.lower)

        #ascvLogger.info(f"Succesfully created dirImageList, dirImageList length: {len(self.dirImageList)}")
        #ascvLogger.debug(f"dirImageList: {self.dirImageList}")

        if hasOpenedImage == 1:
            self.imageNumber = self.dirImageList.index(self.imgFilePath)
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]

    def updateImage(self):
        mwWidth = self.label.frameGeometry().width()
        mwHeight = self.label.frameGeometry().height()

        if self.imgFilePath != "":
            pixmap_ = QtGui.QPixmap(self.imgFilePath)
            pixmap = pixmap_.scaled(mwWidth, mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        self.label.resize(mwWidth, mwHeight)

    def resizeEvent(self, event):
        self.updateImage()

    # I should clean up these two too
    def prevImage(self):
        #ascvLogger.debug(f"Showing previous image, imageNumber = {self.imageNumber}")
        self.imageNumber -= 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

    def nextImage(self):
        #ascvLogger.debug(f"Showing next image, imageNumber = {self.imageNumber}")
        self.imageNumber += 1
        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

    def openLogWin(self):
        self.lw = LogViewer(parent=self)
        self.lw.show()

    def openHelpWin(self):
        self.hw = HelpWindow(parent=self)
        self.hw.show()

    def openAboutWin(self):
        Form = QtWidgets.QWidget()
        self.aw = AboutWindow(Form, parent=self)
        self.aw.show()

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
                #ascvLogger.info("Disabling prompt...")
                config["prompts"]["enableExitPrompt"] = False
            #else:
            #    ascvLogger.info("Not disabling prompt.")

            if x == QtWidgets.QMessageBox.Yes:
                #ascvLogger.info("Exiting...")
                self.onCloseActions()
                event.accept()
            else:
                #ascvLogger.info("Not exiting.")
                event.ignore()

        else:
            #ascvLogger.info("Exit prompt is disabled, exiting...")
            self.onCloseActions()
            event.accept()

class LogViewer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()

        self.resize(600, 400)

        geo = self.geometry()
        geo.moveCenter(self.parent.geometry().center())
        self.setGeometry(geo)

        self.setWindowTitle("Log Viewer")
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        logTextEdit = QtWidgets.QPlainTextEdit(self)
        self.setCentralWidget(logTextEdit)
        logTextEdit.appendPlainText("Coming soon.")

class HelpWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()

        self.resize(725, 460)

        geo = self.geometry()
        geo.moveCenter(self.parent.geometry().center())
        self.setGeometry(geo)

        self.setWindowTitle("Help")
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        self.label = QtWidgets.QLabel(self)
        self.setCentralWidget(self.label)
        self.label.setText("<b>Coming soon.</b><br /><i>In the meantime, check out the repository's Wiki.</i>")

        mainLabelFont = QtGui.QFont()
        mainLabelFont.setPointSize(16)
        self.label.setFont(mainLabelFont)

        self.label.setAlignment(QtCore.Qt.AlignCenter)

# =====================================================
# This class below is a modified version of about.py, a script that was generated by pyuic5.
# That is why the entire thing is big and clunky.

class AboutWindow(QtWidgets.QWidget):
    def __init__(self, Form, parent=None):
        self.parent = parent
        Form = self
        super().__init__()

        Form.resize(900, 502)
        geo = self.geometry()
        geo.moveCenter(self.parent.geometry().center())
        Form.setGeometry(geo)
        
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_3.setSpacing(9)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.image = QtWidgets.QLabel(Form)
        self.image.setMinimumSize(QtCore.QSize(128, 128))
        self.image.setMaximumSize(QtCore.QSize(300, 300))
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap(":/icon/icon"))
        self.image.setScaledContents(True)
        self.image.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.image.setWordWrap(False)
        self.image.setObjectName("image")
        self.verticalLayout_4.addWidget(self.image, 0, QtCore.Qt.AlignTop)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.programName = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.programName.setFont(font)
        self.programName.setTextFormat(QtCore.Qt.PlainText)
        self.programName.setScaledContents(False)
        self.programName.setObjectName("programName")
        self.horizontalLayout_5.addWidget(self.programName)
        spacerItem = QtWidgets.QSpacerItem(8, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.majorReleaseName = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik Semilight")
        font.setPointSize(36)
        self.majorReleaseName.setFont(font)
        self.majorReleaseName.setTextFormat(QtCore.Qt.PlainText)
        self.majorReleaseName.setObjectName("majorReleaseName")
        self.horizontalLayout_5.addWidget(self.majorReleaseName)
        self.horizontalLayout_5.setStretch(2, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.versionLabel = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik Semilight")
        font.setPointSize(18)
        self.versionLabel.setFont(font)
        self.versionLabel.setTextFormat(QtCore.Qt.PlainText)
        self.versionLabel.setObjectName("versionLabel")
        self.verticalLayout_3.addWidget(self.versionLabel)
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setMinimumSize(QtCore.QSize(0, 22))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout_5.setSpacing(4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_9 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        self.label_9.setFont(font)
        self.label_9.setTextFormat(QtCore.Qt.PlainText)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout.addWidget(self.label_9)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.PlainText)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label_10 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(14)
        self.label_10.setFont(font)
        self.label_10.setTextFormat(QtCore.Qt.PlainText)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_2.addWidget(self.label_10)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_5)
        self.line_2 = QtWidgets.QFrame(self.widget)
        self.line_2.setMinimumSize(QtCore.QSize(0, 22))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.label_11 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Selawik")
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_11.setScaledContents(False)
        self.label_11.setWordWrap(True)
        self.label_11.setIndent(-1)
        self.label_11.setOpenExternalLinks(True)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_3.addWidget(self.label_11)
        self.horizontalLayout_3.addWidget(self.widget, 0, QtCore.Qt.AlignTop)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.verticalWidget = QtWidgets.QWidget(Form)
        self.verticalWidget.setMaximumSize(QtCore.QSize(16777215, 96))
        self.verticalWidget.setStyleSheet("background:#3B4252;")
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(24, 24, 24, 24)
        self.horizontalLayout_4.setSpacing(24)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget1 = QtWidgets.QWidget(self.verticalWidget)
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_5 = QtWidgets.QLabel(self.widget1)
        self.label_5.setMinimumSize(QtCore.QSize(16, 16))
        self.label_5.setMaximumSize(QtCore.QSize(16, 16))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/icon/github"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_7.addWidget(self.label_5)
        self.label_4 = QtWidgets.QLabel(self.widget1)
        self.label_4.setTextFormat(QtCore.Qt.RichText)
        self.label_4.setScaledContents(False)
        self.label_4.setOpenExternalLinks(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_7.addWidget(self.label_4)
        self.horizontalLayout_4.addWidget(self.widget1, 0, QtCore.Qt.AlignHCenter)
        self.widget2 = QtWidgets.QWidget(self.verticalWidget)
        self.widget2.setObjectName("widget2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.widget2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.label_6 = QtWidgets.QLabel(self.widget2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.horizontalLayout_4.addWidget(self.widget2, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.gridLayout.addWidget(self.verticalWidget, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.programName.setText(_translate("Form", "AscentViewer"))
        self.majorReleaseName.setText(_translate("Form", "Example"))
        self.versionLabel.setText(_translate("Form", "Version label"))
        self.label.setText(_translate("Form", "Python version"))
        self.label_9.setText(_translate("Form", "0.0.0"))
        self.label_2.setText(_translate("Form", "PyQt5 version"))
        self.label_10.setText(_translate("Form", "0.0.0"))
        self.label_11.setText(_translate("Form", "**AscentViewer** is an **image viewer** written in **Python** using [**PyQt**](https://riverbankcomputing.com/software/pyqt/), and several other libraries."))
        self.label_4.setText(_translate("Form", "<a href=\"https://github.com/despawnedd/AscentViewer/\">GitHub repository</a>"))
        self.label_3.setText(_translate("Form", "Globe icon"))
        self.label_6.setText(_translate("Form", "Website"))
