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

'''
A simple launcher for AscentViewer. Sort of based on "https://github.com/qutebrowser/qutebrowser/blob/master/qutebrowser/__main__.py"
'''

import sys
import os
import subprocess
import platform
import py_compile

try:
    os.chdir(__file__.replace(os.path.basename(__file__), ""))
except:
    pass

# from https://stackoverflow.com/a/6598286/14558305
def my_except_hook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        print("KeyboardInterrupt occurred.")
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = my_except_hook

pyLocation = "AscentViewer-files/ascv_main.py"
pycLocation = "AscentViewer-files/ascv_main.pyc"

print("Compiling AscentViewer...")
# from https://stackoverflow.com/a/5607315/14558305
py_compile.compile(pyLocation, pycLocation)

print("Starting AscentViewer...\n")
# =====================================================
# Note: The code below is kinda messy. Expect a change soon.
if platform.system() == "Windows":
    # Note: You need to have Python launcher installed for this to work.
    subprocess.run(["py", pycLocation])
else:
    # For Unix-based systems. Make sure that Python is either in your PATH, or that it's installed to /usr/bin/python3.
    try:
        subprocess.run(["python3", pycLocation])
    except:
        subprocess.run(["/usr/bin/python3", pycLocation])
