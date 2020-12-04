# thing, gonna remove later
"""
https://riptutorial.com/tkinter/example/31880/treeview--basic-example
https://realpython.com/python-logging/
https://stackoverflow.com/questions/3220284/how-to-customize-the-time-format-for-python-logging
https://www.loggly.com/ultimate-guide/python-logging-basics/
https://medium.com/@KonopkaKodes/an-introduction-to-asynchronous-programming-in-python-6809a4385f69
https://www.geeksforgeeks.org/taking-input-from-console-in-python/
https://stackoverflow.com/questions/16996432/how-do-i-bind-the-enter-key-to-a-function-in-tkinter
https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
# thing, gonna remove later

import tkinter as tk
from tkinter import filedialog
import tkinter.ttk
from PIL import ImageTk, Image
import os
import sys
import glob
import functools
import time
import datetime
from platform import system
import json
import atexit
import logging
import asyncio
import threading

config = json.load(open("data/user/config.json"))

class main:
    def __init__(self, master):
        self.i = 0
        # Clear logs on startup, can be disabled.
        if config["temporary_files"]["clear_logs_on_startup"]:
            files = glob.glob("data/temp/logs/*.*")
            print(files)
            for f in files:
                os.remove(f)
            print("Erased all logs.")
        else:
            pass

        self.date_format_file = "%d%m%Y_%H%M%S"
        self.date_format = "%d/%m/%Y %H:%M:%S"
        
        self.ddiv_logger()

        print(os.path.exists("data/temp/logs"))
        self.master = master
        master.title("DespawnedDiamond's Image Viewer")

        root.bind("<Return>", self.random_print)

        # second_thread.sec_main(second_thread)

    def ddiv_logger(self):
        self.logfile = f"data/temp/logs/log_{datetime.datetime.now().strftime(self.date_format_file)}.txt"
        logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), logging.FileHandler(self.logfile)], format="[%(asctime)s | %(funcName)s | %(levelname)s] %(message)s", datefmt=self.date_format)
        self.logger = logging.getLogger("test_log")

        if not os.path.exists(self.logfile):
            with open(self.logfile, "w") as f:
                f.write("="*15 + "[ BEGIN LOG ]" + "="*15 + "\n") 
        else:
            pass

    def random_print(self, event):
        self.i = self.i + 1
        self.logger.info(f"Hey! I work! Score: {self.i}")

# class second_thread:
#     def sec_main(self):
#         self.loop_enabled = True
#         threading.Thread(target = self.thing).start()
# 
#         atexit.register(self.on_closing)
# 
#         self.thing(second_thread)
#     
#     def on_closing(self):
#         self.loop_enabled = False
# 
#     def thing(self):
#         while self.loop_enabled:
#             time.sleep(2)
#             print("bruh")

root = tk.Tk()
app = main(root)
tk.mainloop()

# - PREVIOUS SOURCE CODE - Only use is to easily port over stuff without having to completely rewrite it again.
# ----------------------------------------------------------------------------
# 
# # importing stuff and defining root as Tk()
# from tkinter import *
# from tkinter import filedialog
# # from tkinter.ttk import *
# import tkinter.ttk
# from PIL import ImageTk, Image
# import os
# import glob
# import functools
# import time
# import datetime
# from platform import system
# from resizeimage import resizeimage
# import json

# import atexit
# import logging
# 
# root = Tk()
# ttk = tkinter.ttk
# 
# config = json.load(open("data/user/config.json"))
# 
# # functions
# def main():
#     global thisdir, scrnW, scrnH, dateFormat, style, filePath, mainImageLabel, prevButton, nextButton, imageInfoLabel, statusBar, style, titleFull
#     print("Debugging stuff:\n")
#     print("\nmain() called")
# 
#     style = ttk.Style()
#     if system() == "Windows":
#         style.theme_use("vista")
#     elif system() == "Darwin":
#         style.theme_use("aqua")
#     else:
#         style.theme_use("clam")
# 
#     thisdir = os.path.dirname(__file__)
# 
#     scrnW = root.winfo_screenwidth()
#     scrnH = root.winfo_screenheight()
# 
#     dateFormat = "Last Modified: %d/%m/%Y, %H:%M:%S"
# 
#     titleFull = "DespawnedDiamond's Image Viewer"
#     titleShort = "DDIV"
# 
#     root.title("DespawnedDiamond's Image Viewer")
#     # icon = PhotoImage(f"{thisdir}/images/icons/duckicon_fXQ_3.ico")
#     # root.iconbitmap(False, icon)
# 
#     mainMenu = Menu(root)
#     root.config(menu=mainMenu)
# 
#     fileMenu = Menu(mainMenu, tearoff=0)
#     mainMenu.add_cascade(label="File", menu=fileMenu)
#     fileMenu.add_command(label="Open Image File", command=openFileDialog)
#     fileMenu.add_command(label="Open Directory", command=openDirDialog)
#     fileMenu.add_separator()
#     fileMenu.add_command(label="Exit", command=root.quit)
# 
#     themeMenu = Menu(mainMenu, tearoff=0)
#     mainMenu.add_cascade(label="Themes", menu=themeMenu)
#     themes = style.theme_names()
#     print(themes)
# 
#     def store_argument(function, arg):
#         return lambda: function(arg)
# 
#     for theme in themes:
#         themeMenu.add_command(label=theme, command=store_argument(style.theme_use, theme))
# 
#     if config["debug"]["enabled"]:
#         debugMenu = Menu(mainMenu, tearoff=0)
#         mainMenu.add_cascade(label="Debug", menu=debugMenu)
#         debugMenu.add_command(label="Print \"winXPos\" and \"winYPos\"", command=WinPosFunc)
# 
#     current_time_f = time.localtime()
#     current_time = time.strftime("[%d/%m/%Y] %H:%M:%S", current_time_f)
# 
#     def delete_tempfile():
#         if os.path.exists("data/temp/tempfile.txt"):
#             print("[Temporary Files Manager] tempfile.txt exists, deleting...")
#             os.remove("data/temp/tempfile.txt")
#         else:
#             print("[Temporary Files Manager] tempfile.txt doesn't exist, proceeding...")
# 
#     atexit.register(delete_tempfile)
# 
#     delete_tempfile()
#     
#     tempfile = open("data/temp/tempfile.txt", "x")
#     tempfile.write(f"Start of tempfile.txt! Current time is: {current_time}")
# 
#     helpMenu = Menu(mainMenu, tearoff=0)
#     mainMenu.add_cascade(label="Help", menu=helpMenu)
#     helpMenu.add_command(label="How to use this program?")
#     helpMenu.add_separator()
#     helpMenu.add_command(label="GitHub page (program)")
#     helpMenu.add_command(label="About", command=aboutWindowFunc)
# 
#     # buttons, labels and the status bar
#     mainImageLabel = Label(root, text="Please open an image or a directory with images.", fg="#135f87",
#                            font=("Segoe UI", 12))
# 
#     btnSeparator = ttk.Separator(root, orient=HORIZONTAL)
#     # btnSeparator = Label(text = "", bd = 1, relief = SUNKEN)
#     prevButton = ttk.Button(root, text="< Previous", command=previousImage)
#     imageInfoLabel = Label(root, text="Open an image or directory.")
#     nextButton = ttk.Button(root, text="Next >", command=nextImage)
# 
#     mainImageLabel.grid(row=0, column=0, columnspan=3)
# 
#     btnSeparator.grid(row=1, column=0, columnspan=3, sticky='we')
#     root.grid_rowconfigure(1, weight=1)
# 
#     prevButton.grid(row=2, column=0, ipady=6)
#     root.grid_columnconfigure(0, weight=1)
# 
#     imageInfoLabel.grid(row=2, column=1)
#     root.grid_columnconfigure(1, weight=1)
# 
#     nextButton.grid(row=2, column=2, ipadx=10, ipady=6)
#     root.grid_columnconfigure(2, weight=1)
# 
#     # funny bar
#     statusBar = Label(bd=1, relief=SUNKEN, anchor=W)
#     sbConfig(0)
#     statusBar.grid(row=3, column=0, columnspan=3, sticky="we")
# 
# 
# def WinPosFunc():
#     print("\nWinPosFunc called")
# 
#     x_pos = root.winfo_x()
#     y_pos = root.winfo_y()
# 
#     print("windowXPos: %s\n windowYPos: %s" % (x_pos, y_pos))
# 
# 
# def aboutWindowFunc():
#     print("\naboutWindowFunc() called")
# 
#     x_pos = root.winfo_x()
#     y_pos = root.winfo_y()
#     aboutWindow = Toplevel(root)
#     aboutWindow.geometry("300x200+%s+%s" % (x_pos, y_pos))
#     aboutWindow.focus_force()
# 
#     mainTitleLabel = Label(aboutWindow, text="DespawnedDiamond's Image Viewer")
#     mainTitleLabel.config(font=("Segoe UI", 12))
#     mainTitleLabel.grid(row=0, column=0)
# 
# 
# def showImage():
#     global mainImage, mainImagePhoto, mainImageLabel, filePath, imageInfoLabel, titleFull
#     print("\nshowImage() called")
# 
#     mainImage = Image.open(filePath)
#     imageW, imageH = mainImage.size
# 
#     root.title(titleFull + " - " + os.path.basename(filePath))
# 
#     if imageW >= round(scrnW / 1.3) and not imageH >= round(scrnH / 1.3):
#         imageWscaled = round(scrnW / 1.3 + .5)
#         mainImage = resizeimage.resize_contain(mainImage, [imageWscaled, round(imageH * (imageWscaled / imageW))])
#     elif imageH >= round(scrnH / 1.3):
#         imageHscaled = round(scrnH / 1.3 + .5)
#         mainImage = resizeimage.resize_contain(mainImage, [round(imageW * (imageHscaled / imageH)), imageHscaled])
# 
#     mainImagePhoto = ImageTk.PhotoImage(mainImage)
# 
#     mainImageLabel.config(text="", image=mainImagePhoto)
#     mainImageLabel.photo = mainImagePhoto
#     mainImageLabel.grid(row=0, column=0, columnspan=3)
# 
#     imageInfoLabel.config(
#         text=f"{os.path.basename(filePath)}, {imageW}x{imageH}\n{datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime(dateFormat)}\n{imageNumber + 1} out of {len(dirImageList)}")
#     sbConfig(0)
# 
#     mainImage.thumbnail((96, 96), Image.LANCZOS)
#     # mainImage_name = os.path.splitext(filePath)[0]
#     mainImage.save(f"data/temp/thumbnails/thumb_{os.path.basename(filePath)}", "PNG")
# 
# def openFileDialog():
#     global filePath, dirPath, imageNumber, hasOpenedImage
#     print("\nopenFileDialog called")
#     sbConfig(1)
#     filePath = filedialog.askopenfilename(title="Select an Image File")
# 
#     if filePath != "":
#         print(f"filePath: \"{filePath}\"")
#         dirPath = filePath.replace(os.path.basename(filePath), "")
#         print(f"dirPath: \"{dirPath}\"")
#         hasOpenedImage = 1
# 
#         dirMakeImageList()
#     else:
#         print("No file specified, filePath is (probably) empty!")
#         sbConfig(0)
# 
# 
# def openDirDialog():
#     global dirPath, hasOpenedImage, statusBar
#     print("\nopenDirDialog called")
#     sbConfig(1)
#     dirPath = filedialog.askdirectory(title="Select a Directory")
#     if dirPath != "":
#         sbConfig(2)
#         print(f"dirPath: \"{dirPath}\"")
#         hasOpenedImage = 0
#         dirMakeImageList()
#     else:
#         print("No directory specified, dirPath is (probably) empty!")
#         sbConfig(0)
# 
# 
# def dirMakeImageList():
#     global dirPath, dirImageList, imageNumber, filePath, statusBar
#     print("\ndirMakeImageList() called")
# 
#     fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
#     dirImageList = []
# 
#     for files in fileTypes:
#         dirImageList.extend(glob.glob(f"{dirPath}/{files}"))
# 
#     dirImageList = [files.replace('\\', '/') for files in dirImageList]
#     dirImageList.sort(key=str.lower)
# 
#     sbConfig(0)
#     print(f"dirImageList: {dirImageList}, dirImageList length: {len(dirImageList)}")
# 
#     if hasOpenedImage == 1:
#         imageNumber = dirImageList.index(filePath)
#     else:
#         imageNumber = 0
# 
#     filePath = dirImageList[imageNumber]
# 
#     buttonCheck()
# 
# 
# def buttonCheck():
#     print("\nbuttonCheck() called")
# 
#     if imageNumber <= 0:
#         prevButton.config(state=DISABLED)
#     elif imageNumber >= 1:
#         prevButton.config(state=NORMAL)
# 
#     if imageNumber >= len(dirImageList) - 1:
#         nextButton.config(state=DISABLED)
#     elif imageNumber <= len(dirImageList) - 2:
#         nextButton.config(state=NORMAL)
# 
#     print(imageNumber)
# 
#     showImage()
# 
# 
# def previousImage():
#     global filePath, imageNumber
#     print("\npreviousImage called")
# 
#     imageNumber -= 1
#     filePath = dirImageList[imageNumber]
# 
#     buttonCheck()
# 
# 
# def nextImage():
#     global filePath, imageNumber
#     print("\nnextImage called")
# 
#     imageNumber += 1
#     filePath = dirImageList[imageNumber]
#     sbConfig(2)
#     buttonCheck()
# 
# 
# def sbConfig(sbState):
#     # sbTextList = [" Ready.", " Waiting...", " Loading..."]
#     # sbColorsList = ["#8fdba9", "#ffc421", "#63bbe0"]
# 
#     if sbState == 0:
#         statusBar.config(text=" Ready.", bg="#8fdba9")
#     if sbState == 1:
#         statusBar.config(text=" Waiting...", bg="#ffca61")
#     if sbState == 2:
#         statusBar.config(text=" Loading...", bg="#63bbe0")
# 
# 
# # mainloop and if __name__ == "__main__"
# if __name__ == "__main__":
#     main()
# 
# root.mainloop()