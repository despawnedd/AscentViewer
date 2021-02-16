# from https://medium.com/@philipp.h/reduce-clutter-when-using-pyinstaller-in-one-directory-mode-b631b9f7f89b

import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'lib'))
sys._MEIPASS=os.path.join(sys._MEIPASS, 'lib')
