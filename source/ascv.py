# =================================
# Thank you for using and/or checking out AscentViewer!
# =================================

from PyQt5 import QtGui, QtCore, QtWidgets
from data.lib.ascv_ui import MainUi, LogViewer, HelpWindow
import sys
import ctypes
import json
import logging
import os
import platform
import glob
import datetime
import signal

if __name__ == '__main__':
    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    ver = "0.0.1_dev-1.1-PyQt5"
    date_format_file = "%d%m%Y_%H%M%S"
    date_format = "%d/%m/%Y %H:%M:%S"

    config = json.load(open("data/user/config.json")) # using json instead of QSettings, for now

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
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ascv") # makes the AscentViewer icon appear in the taskbar, more info here: "https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105"

    signal.signal(signal.SIGINT, signal.SIG_DFL) # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")
    app = QtWidgets.QApplication(sys.argv)

    window = MainUi()
    window.show()
    window.setWindowTitle(f"AscentViewer {ver}")

    sys.exit(app.exec_())
