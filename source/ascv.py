# =====================================================
# Thank you for using and/or checking out AscentViewer!
# =====================================================

import sys
import json
import os
import platform
import signal
import glob

if __name__ == "__main__":
    print("Launching AscentViewer...")

    signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    ver = "0.0.1_dev-3.0-PyQt5"
    date_format_file = "%d%m%Y_%H%M%S"
    date_format = "%d/%m/%Y %H:%M:%S"

    config = json.load(open("data/user/config.json", encoding="utf-8")) # using json instead of QSettings, for now

    print("Deleting logs on statup is ", end="")
    if config["temporary_files"]["logs"]["deleteLogsOnStartup"]:
        print("enabled, erasing all logs...")
        logs = glob.glob("data/user/temp/logs/log*.log")
        for f in logs:
            os.remove(f)
    else:
        print("disabled, not deleting logs.")

    print("Starting logger...")
    from data.lib.ascv_logging import ascvLogger, logIntroLine
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
    from PyQt5 import QtGui, QtCore, QtWidgets
    from data.lib.ascv_main import MainUi

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
