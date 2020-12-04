'''
DespawnedDiamond's Image Viewer
huge thanks to:

tutorials, info and stackoverflow answers I used:
https://www.sololearn.com/Play/Python
https://www.youtube.com/watch?v=YXPyB4XeYLA
https://www.youtube.com/watch?v=ZS2_v_zsPTg
https://stackoverflow.com/questions/47138691/tkinter-image-is-blank
https://stackoverflow.com/questions/7126916/perform-a-string-operation-for-every-element-in-a-python-list
https://stackoverflow.com/questions/4568580/python-glob-multiple-filetypes
https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
https://stackoverflow.com/questions/61485360/opening-a-file-from-other-directory-in-python
https://stackoverflow.com/questions/27639298/tkinter-open-a-new-window-with-a-button-prompt
https://stackoverflow.com/questions/54785138/how-to-access-a-desired-path-with-filedialog-askopenfilename-in-tkinter
https://stackoverflow.com/questions/39555194/how-to-add-space-between-two-widgets-placed-in-grid-in-tkinter-python
https://stackoverflow.com/questions/24644339/python-tkinter-resize-widgets-evenly-in-a-window
https://stackoverflow.com/questions/49598456/vertical-line-tkinter-using-grid
https://stackoverflow.com/questions/37924785/ttk-separator-set-the-length-width
https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
https://stackoverflow.com/questions/46423711/how-to-replace-a-specific-character-in-every-element-of-a-list
https://stackoverflow.com/questions/53580507/disable-enable-button-in-tkinter
https://www.edureka.co/blog/python-list-length/#:~:text=There%20is%20a%20built%2Din,length%20of%20the%20given%20list.
https://stackoverflow.com/questions/6444548/how-do-i-get-the-picture-size-with-pil
https://www.programiz.com/python-programming/methods/list/sort
https://stackoverflow.com/questions/14032521/python-data-structure-sort-list-alphabetically
https://github.com/VingtCinq/python-resize-image
https://www.tutorialspoint.com/python/tk_label.htm#:~:text=To%20display%20one%20or%20more,will%20force%20a%20line%20break.
https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
https://stackoverflow.com/questions/49471004/python-format-ctime-method
https://jaxenter.com/implement-switch-case-statement-python-138315.html

misc. tools:

https://icoconvert.com/

and to my friends, Anthony and Jan!
'''
#----------------------------------------------------------------------------

# importing stuff and defining root as Tk()
from tkinter import *
from tkinter import filedialog
#from tkinter.ttk import *
import tkinter.ttk
from PIL import ImageTk,Image
import os
import glob
import functools
import time
import datetime
from platform import system
from resizeimage import resizeimage

root = Tk()
ttk = tkinter.ttk

# functions
def main():
    global thisdir, scrnW, scrnH, dateFormat, style
    print("Debugging stuff:\n")
    print("\nmain() called")
    
    style = ttk.Style()
    if system() == "Windows":
        style.theme_use("vista")
    elif system() == "Darwin":
        style.theme_use("aqua")
    else:
        style.theme_use("clam")

    thisdir = os.path.dirname(__file__)

    scrnW = root.winfo_screenwidth()
    scrnH = root.winfo_screenheight()

    dateFormat = "Last Modified: %d/%m/%Y, %H:%M:%S"

    mainGUI()

def mainGUI():
    global filePath, mainImageLabel, prevButton, nextButton, imageInfoLabel, statusBar, style, titleFull
    print("\nmainGUI() called")

    titleFull = "DespawnedDiamond's Image Viewer"
    titleShort = "DDIV"
    
    root.title("DespawnedDiamond's Image Viewer")
    #icon = PhotoImage(f"{thisdir}/images/icons/duckicon_fXQ_3.ico")
    #root.iconbitmap(False, icon)

    mainMenu = Menu(root)
    root.config(menu = mainMenu)

    fileMenu = Menu(mainMenu, tearoff = 0)
    mainMenu.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label = "Open Image File", command = openFileDialog)
    fileMenu.add_command(label = "Open Directory", command = openDirDialog)
    fileMenu.add_separator()
    fileMenu.add_command(label = "Exit", command = root.quit)

    themeMenu = Menu(mainMenu, tearoff = 0)
    mainMenu.add_cascade(label="Themes", menu=themeMenu)
    themes = style.theme_names()
    print(themes) 
    def store_argument(function, arg):
        return lambda: function(arg)

    for theme in themes:
      themeMenu.add_command(label=theme, command=store_argument(style.theme_use, theme))
        
    debugMenu = Menu(mainMenu, tearoff = 0)
    mainMenu.add_cascade(label="Debug", menu=debugMenu)
    debugMenu.add_command(label = "Print \"winXPos\" and \"winYPos\"", command = WinPosFunc)

    helpMenu = Menu(mainMenu, tearoff = 0)
    mainMenu.add_cascade(label = "Help", menu=helpMenu)
    helpMenu.add_command(label = "How to use this program?")
    helpMenu.add_separator()
    helpMenu.add_command(label = "GitHub page (program)")
    helpMenu.add_command(label = "About", command = aboutWindowFunc)


    # buttons, labels and the status bar
    mainImageLabel = Label(root, text = "Please open an image or a directory with images.", fg = "#135f87", font = ("Segoe UI", 12))

    btnSeparator = ttk.Separator(root, orient = HORIZONTAL)
    #btnSeparator = Label(text = "", bd = 1, relief = SUNKEN)
    prevButton = ttk.Button(root, text = "< Previous", command = previousImage)
    imageInfoLabel = Label(root, text = "Open an image or directory.")
    nextButton = ttk.Button(root, text = "Next >", command = nextImage)

    mainImageLabel.grid(row = 0, column = 0, columnspan = 3)

    btnSeparator.grid(row = 1, column = 0, columnspan=3, sticky='we')
    root.grid_rowconfigure(1, weight = 1)

    prevButton.grid(row = 2, column = 0, ipady = 6)
    root.grid_columnconfigure(0, weight = 1)

    imageInfoLabel.grid(row = 2, column = 1)
    root.grid_columnconfigure(1, weight = 1)

    nextButton.grid(row = 2, column = 2, ipadx = 10, ipady = 6)
    root.grid_columnconfigure(2, weight = 1)

    #funny bar
    statusBar = Label(bd = 1, relief = SUNKEN, anchor = W)
    sbConfig(0)
    statusBar.grid(row = 3, column = 0, columnspan = 3, sticky = "we")


def WinPosFunc():
    print("\nWinPosFunc called")

    x_pos = root.winfo_x()
    y_pos = root.winfo_y()

    print("windowXPos: %s\n windowYPos: %s"%(x_pos, y_pos))

def aboutWindowFunc():
    print("\naboutWindowFunc() called")

    x_pos = root.winfo_x()
    y_pos = root.winfo_y()
    aboutWindow = Toplevel(root)
    aboutWindow.geometry("300x200+%s+%s"%(x_pos, y_pos))
    aboutWindow.focus_force()

    mainTitleLabel = Label(aboutWindow, text = "DespawnedDiamond's Image Viewer")
    mainTitleLabel.config(font = ("Segoe UI", 12))
    mainTitleLabel.grid(row = 0, column = 0)

def showImage():
    global mainImage, mainImagePhoto, mainImageLabel, filePath, imageInfoLabel, titleFull
    print("\nshowImage() called")

    mainImage = Image.open(filePath)
    imageW, imageH = mainImage.size

    root.title(titleFull + " - " + os.path.basename(filePath))
    
    if imageW >= round(scrnW / 1.3) and not imageH >= round(scrnH / 1.3):
        imageWscaled = round(scrnW / 1.3 + .5)
        mainImage = resizeimage.resize_contain(mainImage, [imageWscaled, round(imageH * (imageWscaled / imageW))])
    elif imageH >= round(scrnH / 1.3):
        imageHscaled = round(scrnH / 1.3 + .5)
        mainImage = resizeimage.resize_contain(mainImage, [round(imageW * (imageHscaled / imageH)), imageHscaled])

    mainImagePhoto = ImageTk.PhotoImage(mainImage)

    mainImageLabel.config(text = "", image=mainImagePhoto)
    mainImageLabel.photo = mainImagePhoto
    mainImageLabel.grid(row = 0, column = 0, columnspan = 3)

    imageInfoLabel.config(text = f"{os.path.basename(filePath)}, {imageW}x{imageH}\n{datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime(dateFormat)}\n{imageNumber + 1} out of {len(dirImageList)}")
    sbConfig(0)

def openFileDialog():
    global filePath, dirPath, imageNumber, hasOpenedImage
    print("\nopenFileDialog called")
    sbConfig(1)
    filePath = filedialog.askopenfilename(title = "Select an Image File")

    if filePath != "":
        print(f"filePath: \"{filePath}\"")
        dirPath = filePath.replace(os.path.basename(filePath), "")
        print(f"dirPath: \"{dirPath}\"")
        hasOpenedImage = 1

        dirMakeImageList()
    else:
        print("No file specified, filePath is (probably) empty!")
        sbConfig(0)

def openDirDialog():
    global dirPath, hasOpenedImage, statusBar
    print("\nopenDirDialog called")
    sbConfig(1)
    dirPath = filedialog.askdirectory(title = "Select a Directory")
    if dirPath != "":
        sbConfig(2)
        print(f"dirPath: \"{dirPath}\"")
        hasOpenedImage = 0
        dirMakeImageList()
    else:
        print("No directory specified, dirPath is (probably) empty!")
        sbConfig(0)

def dirMakeImageList():
    global dirPath, dirImageList, imageNumber, filePath, statusBar
    print("\ndirMakeImageList() called")

    fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
    dirImageList = []

    for files in fileTypes:
        dirImageList.extend(glob.glob(f"{dirPath}/{files}"))

    dirImageList = [files.replace('\\', '/') for files in dirImageList]
    dirImageList.sort(key=str.lower)

    sbConfig(0)
    print(f"dirImageList: {dirImageList}, dirImageList length: {len(dirImageList)}")

    if hasOpenedImage == 1:
        imageNumber = dirImageList.index(filePath)
    else:
        imageNumber = 0

    filePath = dirImageList[imageNumber]

    buttonCheck()

def buttonCheck():
    print("\nbuttonCheck() called")

    if imageNumber <= 0:
        prevButton.config(state = DISABLED)
    elif imageNumber >= 1:
        prevButton.config(state = NORMAL)

    if imageNumber >= len(dirImageList) - 1:
        nextButton.config(state = DISABLED)
    elif imageNumber <= len(dirImageList) - 2:
        nextButton.config(state = NORMAL)

    print(imageNumber)

    showImage()
   
def previousImage():
    global filePath, imageNumber
    print("\npreviousImage called")

    imageNumber -= 1
    filePath = dirImageList[imageNumber]

    buttonCheck()

def nextImage():
    global filePath, imageNumber
    print("\nnextImage called")

    imageNumber += 1
    filePath = dirImageList[imageNumber]
    sbConfig(2)
    buttonCheck()

def sbConfig(sbState):
    #sbTextList = [" Ready.", " Waiting...", " Loading..."]
    #sbColorsList = ["#8fdba9", "#ffc421", "#63bbe0"]

    if sbState == 0:
        statusBar.config(text = " Ready.", bg = "#8fdba9")
    if sbState == 1:
        statusBar.config(text = " Waiting...", bg = "#ffca61")
    if sbState == 2:
        statusBar.config(text = " Loading...", bg = "#63bbe0")

# mainloop and if __name__ == "__main__"
if __name__ == "__main__":
    main()

root.mainloop()
