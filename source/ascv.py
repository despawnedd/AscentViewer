# =====================================================
# Thank you for using and/or checking out AscentViewer!
# =====================================================

from PyQt5 import QtGui, QtCore, QtWidgets
from ascv_main import MainUi
import sys
import json
import logging
import os
import platform
import glob
import datetime
import signal

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")

    try:
        newchdir = __file__.replace(os.path.basename(__file__), "")
        os.chdir(newchdir) # thanks to Anthony for this
    except:
        pass

    ver = "0.0.1_dev-2.0-PyQt5"
    date_format_file = "%d%m%Y_%H%M%S"
    date_format = "%d/%m/%Y %H:%M:%S"

    config = json.load(open("data/user/config.json", encoding="utf-8")) # using json instead of QSettings, for now

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
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(119, 124, 193))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(119, 124, 193))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
    app.setPalette(dark_palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = MainUi()
    window.show()

    sys.exit(app.exec_())
