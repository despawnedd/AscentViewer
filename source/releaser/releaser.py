# A script that uses auto-py-to-exe and PyInstaller to export a Windows executable from the source code.

import sys
import os
import subprocess

class MainExporter:
    def __init__(self):
        # from https://stackoverflow.com/a/24595376/14558305
        #proc = subprocess.Popen("python --version", stdout=subprocess.PIPE, shell=True)
        #(out, err) = proc.communicate()
        #expLogger.info(out)

        subprocess.run("pyinstaller --noconfirm --onedir --console --icon \"icon3_UaA_icon.ico\" --name \"AscentViewer\" --add-data \"../data;data/\"  \"../ascv.py\"")

if __name__ == "__main__":
    print("This script might make some changes to your system. Are you sure you want to continue? (y/yes/n/no)\n> ", end="")
    answer = input().lower()

    if answer == "y" or answer == "yes":
        print("Okay, continuing script...")
    elif answer == "n" or answer == "no":
        print("Okay, cancelling script...")
        exit()

    # I like to force-delete variables that will not be used anymore.
    del answer 

    from lib.rlsr_logging import *

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), ""))
    except:
        pass

    MainExporter()
