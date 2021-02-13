from PyQt5 import QtGui, QtCore, QtWidgets
import json
import glob
import os
import shutil
import platform
import pkg_resources

from data.lib.ascv_logging import * # how does this work but the "config =" line doesn't without line 13 on Linux

try:
    os.chdir(os.path.abspath(__file__.replace(os.path.basename(__file__), "../..")))
except:
    pass

ver = "0.0.1_dev-2.1-PyQt5"
config = json.load(open("data/user/config.json", encoding="utf-8"))

lang = config["localization"]["lang"]
localization = json.load(open(f"data/assets/localization/lang/{lang}.json", encoding="utf-8"))

class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # =====================================================
        # non-gui related stuff:

        self.dirPath = ""
        self.imgFilePath = ""
        self.saveConfigOnExit = True

        # =====================================================
        # gui related stuff:

        ascvLogger.info("Initializing GUI.")
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

        self.setWindowTitle(f"AscentViewer")
        self.resize(config["windowProperties"]["width"], config["windowProperties"]["height"])
        self.move(config["windowProperties"]["x"], config["windowProperties"]["y"])
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3.png"))

        self.statusBar().setStyleSheet("background: #777CC1;")

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
        ascvLogger.info("GUI has been initialized.")

    def dumpJson(self):
        with open("data/user/config.json", "w", encoding="utf-8", newline="\n") as cf:
            json.dump(config, cf, ensure_ascii=False, indent=4)
            cf.write("\n") # https://codeyarns.com/tech/2017-02-22-python-json-dump-misses-last-newline.html

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

            self.imgFilePath = self.dirImageList_[self.imageNumber]

            self.updateImage()
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
        else:
            ascvLogger.info(f"Succesfully created dirImageList_, but it's empty! Not setting dirImageList to dirImageList_")

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
        ascvLogger.debug(f"Showing previous image, imageNumber = {self.imageNumber}")
        if self.imageNumber != 0:
            self.imageNumber -= 1
        else:
            self.imageNumber = len(self.dirImageList) - 1

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

    def nextImage(self):
        ascvLogger.debug(f"Showing next image, imageNumber = {self.imageNumber}")
        if self.imageNumber != len(self.dirImageList) - 1:
            self.imageNumber += 1
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateImage()

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
        # This code below is a modified version of about.py, a script that was generated by pyuic5.
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
