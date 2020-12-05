# DespawnedDiamond's Image Viewer (DDIV)

**DespawnedDiamond's Image Viewer**, **DDIV** for short, is an **image viewer** program written in **Python**. It's based on [this Tkinter tutorial](https://www.youtube.com/watch?v=zg4c92pNFeo), and [many other resources](/CREDITS.md).

[//]: # (DDIV's successor, AscentViewer is available here: [AscentViewer's GitHub Page].)
[//]: # (It is written using C# and XAML instead of Python for a cleaner and better user experience.)

DDIV's [website](https://despawnedd.acrazytown.com/ddiv).

## New DDIV 

As you may know we've seperated DDIV into 2 versions: **Legacy** and **New**.
**Legacy DDIV** is every version of DDIV up to **0.1.0.9**.
**New DDIV** is a complete rewrite of DDIV using **[PyQT](https://riverbankcomputing.com/software/pyqt/)** and classes.

Due to the PyQT's GUI designer, new builds of DDIV should come out quicker than Legacy DDIV, as you simply drag-n-drop to build a GUI.

### New DDIV Status

As of December 5th 2020, **New DDIV** is **0%** finished.

Current status: 
Development not started yet.
## Requirements

- [PIL/Pillow (ImageTk, Image functions)](https://github.com/python-pillow/Pillow)
- [resizeimage/python-resize-image](https://github.com/VingtCinq/python-resize-image)
- [Python 3.7+](https://www.python.org/downloads/)

## How to run?

### Windows

1. Install Python 3.7+ from [here](https://www.python.org/downloads/)
2. `py -m pip install -r requirements.txt` (or `pip install -r requirements.txt` if you installed Python on PATH)
3. Run DDIV.py

### macOS

macOS usually comes with a copy of Python but that's an old version which isn't supported.

The procedure is the same as on Windows:

1. 1. Install Python 3.7+ from [here](https://www.python.org/downloads/)
2. `python3 -m pip install -r requirements.txt`
3. Run DDIV.py

### Linux

1. Run install.sh
2. `python3 -m pip install -r requirements.txt`
3. Run DDIV.py

## Version naming info

### Version Structure (a.b.c-bld-rev_rl)

"**a**" is the **major version** number (e.g. "**1.0.0**").

"**b**" is the **minor version** number (e.g. "**1.3.0**").

"**c**" is the **match version** number (e.g. "**1.3.8**").

"**bld**" is the **build version** number (e.g. "**1.3.8-201204**") (*The build number's pretty much the date the "build" was made in, formatted like this: last two digits of the  year + month + day*).

"**rev**" is the **revision number** of that build. This will only be used in cases that there are several builds in on day. (e.g. "**1.3.8-201204-4**").

"**rl**" is the **release branch** indicator (eg. "**1.3.8-201204_master**")
