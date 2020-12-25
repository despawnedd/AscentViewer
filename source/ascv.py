import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

def window():
    global label
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 200, 300, 300)
    win.setWindowTitle("Test")

    label = QtWidgets.QLabel(win)
    label.setText("Test")
    #label.move(50, 0)

    b1 = QtWidgets.QPushButton(win)
    b1.setText("Test")
    b1.move(0, 40)
    b1.clicked.connect(clicked)

    win.show()
    sys.exit(app.exec_())

def clicked():
    label.setText("I changed!")

window()
